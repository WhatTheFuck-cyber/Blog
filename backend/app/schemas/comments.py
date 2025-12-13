# app/schemas/comments.py

from imports import BaseModel, Optional, datetime, Field
from .minimal import UserMinimal, ArticleMinimal



class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., description="评论内容")



class CommentCreate(CommentBase):
    """创建评论请求模型"""
    article_id: int = Field(..., description="评论文章ID")
    parent_id: Optional[int] = Field(None, description="父评论ID")



class CommentUpdate(CommentBase):
    """更新评论请求模型"""
    pass



class Comment(CommentBase):
    """评论响应模型"""
    id: int = Field(..., description="评论ID")
    user_id: int = Field(..., description="评论用户ID")
    user_name: str = Field(..., description="评论用户名")
    parent_id: Optional[int] = Field(None, description="父评论ID")
    created_at: datetime = Field(..., description="创建时间戳")
    # 关联「用户/文章极简模型」
    user: Optional["UserMinimal"] = Field(None, description="评论用户")
    article: Optional["ArticleMinimal"] = Field(None, description="评论文章")
    
    class Config:
        from_attributes = True



__all__ = ["CommentBase", "CommentCreate", "CommentUpdate", "Comment"]