# app/schemas/token.py

from imports import BaseModel, Field



class TokenRefresh(BaseModel):
    """令牌刷新请求模型"""
    token: str = Field(..., description="刷新后的令牌")



class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问凭证")
    token_type: str = Field(..., description="令牌认证类型")
    expires_in: int = Field(..., description="令牌过期时间")
    token_refresh_threshold: int = Field(..., description="令牌刷新阈值")



__all__ = ["TokenRefresh", "LoginResponse"]