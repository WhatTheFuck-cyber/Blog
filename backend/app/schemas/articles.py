# app/schemas/articles.py

from imports import BaseModel, Optional, datetime, Field
from .minimal import CommentMinimal



class ArticleBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., min_length=1, max_length=100, description="文章标题，1-100个字符")
    content: str = Field(..., description="文章内容，不能超过数据库限制（开发阶段先不管）")



class ArticleCreate(ArticleBase):
    """创建文章请求模型"""
    pass



class ArticleUpdate(ArticleBase):
    """更新文章请求模型"""
    pass



class Article(ArticleBase):
    """文章响应模型"""
    id: int = Field(..., description="文章ID")
    owner_id: int = Field(..., description="文章作者ID")
    owner_name: str = Field(..., description="文章作者名")
    created_at: datetime = Field(..., description="创建时间戳")
    # 关联「评论极简模型」和分类
    comments: Optional[list["CommentMinimal"]] = Field(None, description="文章下的评论列表")
    category_id: Optional[int] = Field(None, description="文章所属分类ID")
    
    class Config:
        from_attributes = True



class ArticleWithStats(Article):
    """扩展文章模型，包含点赞/收藏状态"""
    like_count: int = 0
    collect_count: int = 0
    is_liked: Optional[bool] = Field(False, description="当前用户是否已点赞")
    is_collected: Optional[bool] = Field(False, description="当前用户是否已收藏")



__all__ = ["ArticleBase", "ArticleCreate", "ArticleUpdate", "Article", "ArticleWithStats"]