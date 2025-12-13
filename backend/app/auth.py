# app/auth.py

from imports import (
    Optional, Union, uuid,
    CryptContext, JWTError, jwt, datetime, timedelta,
    timezone, HTTPException, status, Depends, Request,
    HTTPBearer, HTTPAuthorizationCredentials, logging, os, Session
)

from .database import get_db
from .models import User, TokenBlacklist
from .utils import get_current_utc_time



# -------------------------- 全局配置 --------------------------
# 安全提示：生产时应当从环境变量读取密钥，并删除默认值
# 在启动前运行 cmd 命令：set SECRET_KEY=your-secret-key
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
logger = logging.getLogger(__name__)

# 配置密码哈希上下文
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")



# -------------------------- 令牌相关 --------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配哈希值"""
    return pwd_context.verify(plain_password, hashed_password)



def get_password_hash(password: str) -> str:
    """生成密码的哈希值（无72字节限制）"""
    if not password or password.strip() == "":
        raise ValueError("密码不能为空，且不能全为空格")
    return pwd_context.hash(password)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    # 复制输入数据，避免修改原始字典
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = get_current_utc_time() + expires_delta
    else:
        expire = get_current_utc_time() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 在要编码的数据中添加过期时间字段（exp是JWT标准字段）
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # 每个令牌的唯一标识
    })

    # 将整个数据字典（包括添加的exp字段）编码为JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_and_refresh_token(token: str, db: Session, time_tolerance: int = 120):
    """验证令牌时自动刷新即将过期的令牌"""
    payload = verify_token(token, db)
    
    if payload is None:
        return None  # 令牌完全过期，需要重新登录
    
    # 检查令牌是否即将过期
    expire_timestamp = payload.get("exp")
    current_time = datetime.now(timezone.utc).timestamp()
    
    if expire_timestamp - current_time < time_tolerance:
        # 自动生成新令牌
        new_token = create_access_token({"sub": payload["sub"]})
        return {"payload": payload, "new_token": new_token, "needs_refresh": True}
    
    return {"payload": payload, "needs_refresh": False}



def verify_token(token: str, db: Session) -> Union[dict, None]:
    """
    验证JWT令牌并返回payload，新增黑名单检查
    - 若令牌无效/过期/在黑名单中，返回None
    - 否则返回解码后的payload
    """
    try:
        # 1. 解码令牌（验证密钥和过期时间）
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. 提取令牌唯一标识jti（必须在生成令牌时添加jti字段）
        jti = payload.get("jti")
        if not jti:
            return None  # 缺少jti的令牌视为无效
        
        # 3. 检查令牌是否在黑名单中
        blacklisted_token = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        if blacklisted_token:
            return None  # 令牌已注销，返回无效
        
        # 4. 验证通过，返回payload
        return payload
    
    except JWTError:
        # 令牌解码失败（无效签名/过期等）
        return None



def refresh_token(token: str, expires_delta: Optional[timedelta] = None) -> Union[str, None]:
    """刷新JWT令牌"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    # 移除过期时间
    payload.pop("exp", None)
    
    # 创建新令牌
    return create_access_token(payload, expires_delta)



# -------------------------- 身份校验 --------------------------



oauth2_scheme = HTTPBearer(auto_error=False)



def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    request: Request = None  # 添加请求对象
):
    """从JWT令牌获取当前用户，支持自动刷新（new_token的生产者）"""
    if not credentials: # 支持匿名访问
        return None
    
    token = credentials.credentials
    
    # 使用自动刷新功能验证令牌
    result = verify_and_refresh_token(token, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从令牌中获取用户信息
    email = result["payload"].get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # 从数据库获取用户
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # 如果需要刷新，将新令牌添加到响应头
    if result.get("needs_refresh") and hasattr(request, "state"):
        request.state.new_token = result["new_token"]
    
    return user