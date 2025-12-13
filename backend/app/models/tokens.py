# app/models/tokens.py

"""令牌黑名单模型：管理已注销的JWT令牌，防止复用"""
from .base import (
    Column, Integer, String, DateTime,
    Base, get_current_utc_time
)



class TokenBlacklist(Base):
    """
    令牌黑名单模型
    对应数据库表：token_blacklist
    
    字段说明：
    - id: 主键ID，自动生成
    - jti: JWT唯一标识（唯一、索引，非空）
    - expires_at: 令牌过期时间（用于自动清理过期记录）
    - created_at: 加入黑名单时间（默认当前UTC时间）
    """
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)



__all__ = ["TokenBlacklist"]