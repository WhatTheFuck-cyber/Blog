# app/schemas/categories.py

from imports import BaseModel, Field, Optional, datetime
from .minimal import ArticleMinimal



class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称，1-50个字符")
    description: Optional[str] = Field(None, max_length=200, description="分类描述，最多200个字符")



class CategoryCreate(CategoryBase):
    pass



class Category(CategoryBase):
    id: int = Field(..., description="分类ID")
    created_at: datetime = Field(..., description="创建时间戳")
    articles: Optional[list["ArticleMinimal"]] = Field(None, description="分类下的文章列表")
    
    class Config:
        from_attributes = True



__all__ = ["CategoryBase", "CategoryCreate", "Category"]