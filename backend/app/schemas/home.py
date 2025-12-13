# app/schemas/home.py

from imports import BaseModel, Field
from .categories import Category
from .minimal import ArticleMinimal



class ArticleMinimalWithCounts(ArticleMinimal):
    """带点赞/收藏数的文章极简模型（继承自原有模型）"""
    like_count: int = Field(0, description="文章点赞数")
    collect_count: int = Field(0, description="文章收藏数")


class HomeResponse(BaseModel):
    """主页响应模型，包含文章和分类数据"""
    categories: list["Category"] = Field(..., description="分类列表")
    latest_articles: list["ArticleMinimalWithCounts"] = Field(..., description="最新文章列表")
    
    class Config:
        from_attributes = True



__all__ = ["HomeResponse"]