# app/schemas/users.py

from imports import BaseModel, EmailStr, Field, field_validator, Optional, re, datetime
from .minimal import ArticleMinimal, ArticleMinimalWithStats, CommentMinimal



class UserBase(BaseModel):
    """用户基础模型，包含公共字段"""
    email: EmailStr =  Field(..., description="用户邮箱，唯一，需符合邮箱格式")



class UserCreate(BaseModel):
    """创建用户请求模型（保留原有验证逻辑）"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名（2-50字符，仅字母、数字、下划线）")
    email: EmailStr = Field(..., description="用户邮箱，唯一，需符合邮箱格式")
    password: str = Field(..., min_length=6, description="密码（至少6字符，仅允许字母、数字、!、@、#、$、%、.）")

    @field_validator("password")
    def password_not_blank(cls, v):
        if not v or v.strip() == "":
            raise ValueError("密码不能为空，且不能全为空格")
        return v

    @field_validator("password")
    def password_valid_chars(cls, v):
        valid_pattern = r"^[a-zA-Z0-9!@#$%*.]+$"
        if not re.match(valid_pattern, v):
            raise ValueError("密码仅允许包含字母、数字、!、@、#、$、%、*、.")
        return v

    @field_validator("password")
    def password_complexity(cls, v):
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("密码必须包含至少一个字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含至少一个数字")
        if not re.search(r"[!@#$%*]", v):
            raise ValueError("密码必须包含至少一个特殊符号（!、@、#、$、%、*）")
        return v



class User(UserBase):
    """用户响应模型"""
    id: int =  Field(..., description="用户ID")
    is_active: bool = Field(..., description="用户是否激活")
    activate_at: Optional[datetime] = Field(..., description="激活时间戳")
    # 关联「文章/评论极简模型」
    articles: Optional[list["ArticleMinimal"]] = Field(None, description="用户文章列表，返回极简模型")
    comments: Optional[list["CommentMinimal"]] = Field(None, description="用户评论列表，返回极简模型")
    
    class Config:
        from_attributes = True



class UserInfo(User):
    """用户信息响应模型 - 扩展文章列表字段"""
    username: str = Field(..., description="用户名")
    # 核心修改：覆盖父类的articles字段，使用带点赞/收藏数的扩展模型
    articles: Optional[list["ArticleMinimalWithStats"]] = Field(None, description="用户文章列表（含点赞/收藏数）")

    class Config:
        from_attributes = True



class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="密码")



class UserSearch(User):
    """用户搜索响应模型"""
    username: str = Field(..., description="用户名")

    class Config:
        from_attributes = True



__all__ = ["UserBase", "UserCreate", "User", "UserLogin", "UserSearch", "UserInfo"]