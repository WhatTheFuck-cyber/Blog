# app/schemas/minimal.py

from imports import BaseModel, EmailStr, Optional, datetime, Field



class UserMinimal(BaseModel):
    """用户极简模型：仅返回核心信息，无任何关联"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    
    class Config:
        from_attributes = True



class ArticleMinimal(BaseModel):
    """文章极简模型：仅返回核心信息，无任何关联"""
    id: int = Field(..., description="文章ID")
    title: str = Field(..., description="文章标题")
    owner_id: int = Field(..., description="文章作者ID")
    owner_name: str = Field(..., description="文章作者名")
    created_at: datetime = Field(..., description="创建时间戳")
    
    class Config:
        from_attributes = True



class CommentMinimal(BaseModel):
    """评论极简模型：仅返回核心信息，无任何关联"""
    id: int = Field(..., description="评论ID")
    content: str = Field(..., description="评论内容")
    user_name: str = Field(..., description="评论用户名")
    user_id: int = Field(..., description="评论用户ID")
    article_id: int = Field(..., description="评论文章ID")
    parent_id: Optional[int] = Field(None, description="父评论ID")
    created_at: datetime = Field(..., description="创建时间戳")
    
    class Config:
        from_attributes = True



class ArticleMinimalWithStats(ArticleMinimal):
    """扩展版极简文章模型 - 仅用于UserInfo，增加点赞/收藏数"""
    like_count: int = Field(..., description="文章点赞数量")
    collect_count: int = Field(..., description="文章收藏数量")



__all_ = ["UserMinimal", "ArticleMinimal", "CommentMinimal", "ArticleMinimalWithStats"]