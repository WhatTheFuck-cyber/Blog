# main.py

from imports import (
    FastAPI, Request, HTTPException, JSONResponse, os, sys, signal, asyncio,
    CORSMiddleware, asynccontextmanager, logging, json, uvicorn
)
from app.routers import users, articles, comments, categories, home, search, messages, interactions



# -------------------------- 配置日志 --------------------------
logging.basicConfig(
    level=logging.ERROR,                    # 只记录错误级别日志
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]      # 输出到控制台
)
logger = logging.getLogger("blog_api")      # 定义日志器名称



# -------------------------- 定义 lifespan 上下文管理器 --------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：创建数据库表
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功（通过 lifespan）")
    yield  # 应用运行期间
    # 关闭时：清理资源（根据实际需求添加）
    print("应用开始关闭，执行清理操作...")
    engine.dispose()  # 关闭连接池，释放资源
    print("清理完成，应用已关闭")



# -------------------------- 创建 FastAPI 实例 --------------------------
app = FastAPI(
    title="Blog API",
    version="1.0.0",
    lifespan=lifespan  # 绑定 lifespan
)



# -------------------------- CORS 中间件 --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------------------------- 令牌刷新中间件 --------------------------
@app.middleware("http")
async def token_refresh_middleware(request: Request, call_next):
    """令牌刷新中间件：同时在响应头和响应体中返回新令牌"""
    response = await call_next(request)
    
    # 检查是否有新令牌需要返回
    if hasattr(request.state, "new_token"):
        new_token = request.state.new_token
        # 1. 添加到响应头（保持原有逻辑）
        response.headers["X-New-Access-Token"] = new_token
        
        # 2. 添加到响应体（仅对JSON响应生效）
        if response.media_type == "application/json":
            # 读取原始响应体内容
            body = await response.body()
            try:
                # 解析为JSON字典
                response_data = json.loads(body)
                # 添加新令牌字段（与头字段保持一致，便于前端识别）
                response_data["new_token"] = new_token
                # 构建新的JSON响应（保留原始状态码、头信息）
                return JSONResponse(
                    content=response_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            except json.JSONDecodeError:
                # 若响应体不是有效JSON，不修改（避免破坏响应）
                pass
    
    return response



# -------------------------- 全局异常处理器 --------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理手动抛出的HTTPException"""
    logger.error(
        f"HTTPException | 请求路径：{request.url.path} | 错误信息：{str(exc)}",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,    # 状态码
            "message": exc.detail,      # 错误提示（对用户友好）
            "success": False,           # 标识请求是否成功
            "data": None                # 数据字段统一为None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常（兜底）"""
    # 1. 记录详细错误（含堆栈）到控制台/日志文件
    logger.error(
        f"未捕获的异常 | 请求路径：{request.url.path} | 错误信息：{str(exc)}",
        exc_info=True  # 打印完整堆栈信息
    )
    # 2. 返回用户友好的响应
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后再试",  # 不暴露具体错误
            "success": False,
            "data": None
        }
    )



# -------------------------- 路由挂载 --------------------------
app.include_router(home.router, prefix="/home", tags=["home"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])

# 根路由
@app.get("/")
def read_root():
    return {"message": "Blog API is running!"}



# -------------------------- 服务关闭设置 --------------------------
running = True

def handle_shutdown(sig, frame):
    """处理终止信号（Ctrl+C）"""
    global running
    running = False
    print("\n[INFO] 正在优雅关闭服务...")
    # 停止所有异步任务
    loop = asyncio.get_event_loop()
    loop.stop()
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器（捕获Ctrl+C）
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)  # 兼容Linux/Mac的终止信号
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8888,
            reload=True,
            ssl_keyfile=os.path.join(current_dir, ".key/key.pem"),
            ssl_certfile=os.path.join(current_dir, ".key/cert.pem"),
            log_level="info"
        )
    except (KeyboardInterrupt, SystemExit):
        # 捕获终止异常，不打印堆栈
        print("[INFO] 服务已成功关闭")