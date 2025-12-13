# app/routers/users.py

from imports import (
    APIRouter, Depends, HTTPException, status, Session,
    jwt, time, Optional, EmailStr, datetime, timezone, logging
)

from .. import schemas, models, auth
from ..database import get_db
from ..auth import get_current_user, verify_and_refresh_token
from ..utils import get_current_utc_time

logging.basicConfig(
    level=logging.ERROR,                    # 只记录错误级别日志
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]      # 输出到控制台
)
logger = logging.getLogger("blog_api")      # 定义日志器名称


# 创建认证相关的路由
router = APIRouter()



@router.post("/register", response_model=schemas.User)      # 这是一个响应模型，用于过滤返回给客户端的数据
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """用户注册接口"""
    try:

        # 检查邮箱是否已被注册
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if not user.password or user.password.strip() == "":
            raise ValueError("密码不能为空，且不能全为空格")
        

        # 对密码进行哈希运算
        hashed_password = auth.get_password_hash(user.password)
        
        if user.email == None:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # 创建新用户对象
        new_user = models.User(
            email=user.email, 
            username=user.username, 
            hashed_password=hashed_password,
            activate_at=get_current_utc_time()
        )
        
        # 将新用户添加到数据库
        db.add(new_user)
        db.commit()  # 提交事务
        db.refresh(new_user)  # 刷新对象以获取数据库生成的ID等字段
        
        # 返回新创建的用户信息（通过response_model过滤敏感信息）
        return new_user

    except Exception as e:
        db.rollback()  # 事务回滚
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败：{str(e)}"  # 生产环境改为"服务器内部错误"
        )
    


@router.get("", response_model=schemas.UserInfo)
def get_user(
    user_id: Optional[int] = None,
    email: Optional[EmailStr] = None,
    username: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    根据用户ID、邮箱或用户名查询用户（三选一）
    - 仅返回用户基础信息（ID、用户名、邮箱）
    - 需登录后才能调用（无论查询自己还是他人）
    - 文章列表增加点赞数、收藏数
    """
    # 校验查询参数
    if not any([user_id, email, username]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供 user_id、email 或 username 中的至少一个参数"
        )
    
    # 构建查询条件
    query = db.query(models.User)
    if user_id:
        query = query.filter(models.User.id == user_id)
    if email:
        query = query.filter(models.User.email == email)
    if username:
        query = query.filter(models.User.username == username)
    
    # 执行查询（只返回活跃用户）
    user = query.filter(models.User.is_active == True).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到符合条件的用户"
        )

    # 核心补充：为用户的每篇文章补充点赞数、收藏数
    if user.articles:
        for article in user.articles:
            # 假设你的数据库模型中有：
            # - Article模型关联Like表，可通过count()统计点赞数
            # - Article模型关联Collect表，可通过count()统计收藏数
            article.like_count = db.query(models.Like).filter(models.Like.article_id == article.id).count()
            article.collect_count = db.query(models.Collect).filter(models.Collect.article_id == article.id).count()

    return user



@router.post("/login")
def login_user(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """用户登录接口"""
    try:
        # 根据邮箱查询用户
        user = db.query(models.User).filter(models.User.email == form_data.email, models.User.is_active == True).first()
        
        # 验证用户是否存在且密码正确
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成JWT访问令牌，主题(sub)设置为用户邮箱
        access_token = auth.create_access_token({"sub": user.email})


        payload = jwt.decode(access_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        expires_in = payload["exp"] - int(time.time())
        
        return {
            "user_id": user.id,
            "access_token": access_token, 
            "token_type": "Bearer",
            "expires_in": expires_in,  # 令牌剩余秒数
            "token_refresh_threshold": 120  # 提前120秒刷新
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败：{str(e)}"
        )



@router.post("/logout")
def logout(
    token: schemas.TokenRefresh,  # 复用TokenRefresh模型（接收token字段）
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # 确保用户已登录（验证令牌有效性）
):
    """用户登出接口：将当前访问令牌加入黑名单，使其失效"""
    try:
        # 解码令牌，获取jti（唯一标识）和过期时间
        payload = jwt.decode(
            token.token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM]
        )
        jti = payload.get("jti")  # 获取令牌唯一标识
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)  # 转换为UTC时间
        
        if not jti:
            raise HTTPException(status_code=400, detail="无效的令牌：缺少唯一标识")
        
        # 检查令牌是否已在黑名单中
        existing = db.query(models.TokenBlacklist).filter(models.TokenBlacklist.jti == jti).first()
        if existing:
            return {"message": "令牌已失效"}
        
        # 将令牌加入黑名单
        blacklist_entry = models.TokenBlacklist(
            jti=jti,
            expires_at=expires_at
        )
        db.add(blacklist_entry)
        db.commit()
        
        return {"message": "登出成功，令牌已失效"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败：{str(e)}"
        )



@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """用户注销（销毁）账号接口"""
    
    try:
    # 只能操作自己的账号
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this account"
            )
        
        # 获取要删除的用户
        user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 生成唯一标识符（使用时间戳和用户ID）
        timestamp = int(get_current_utc_time().timestamp())
        unique_suffix = f"{timestamp}_{user_id}"
        
        # 修改用户名和邮箱，释放唯一约束
        user_to_delete.username = f"注销用户_{unique_suffix}"
        user_to_delete.email = None  # 邮箱置空，释放邮箱地址
        
        # 清空用户相关的密码哈希值
        user_to_delete.hashed_password = "deactivated"
        
        # 设置账号为未激活状态
        user_to_delete.is_active = False
        user_to_delete.deactivated_at = get_current_utc_time()
        
        db.commit()
        
        return {"message": "注销成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败：{str(e)}"
        )



# -------------------------- 手动刷新令牌，保存功能 --------------------------
@router.post("/refresh")
def refresh_token_endpoint(refresh_request: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """专门用于刷新令牌的端点：在响应体中返回新令牌"""
    try:
        result = verify_and_refresh_token(refresh_request.token, db)
        
        if result is None:
            # Token无效/过期 → 返回401，而非500
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        if result.get("needs_refresh"):
            return {
                "access_token": result["new_token"],
                "new_token": result["new_token"],
                "token_type": "Bearer",
                "refresh_occurred": True
            }
        else:
            return {
                "access_token": refresh_request.token,
                "new_token": refresh_request.token,
                "token_type": "Bearer",
                "refresh_occurred": False
            }
    # 只捕获「非预期的代码Bug」→ 返回500
    except HTTPException:
        # 主动抛出的401直接向上抛
        raise
    except Exception as e:
        # 记录具体异常日志，方便排查
        logger.error(f"刷新令牌非预期错误：{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误，请稍后重试"
        )