# app/models/categories.py

"""文章分类模型：管理文章的分类体系"""
from .base import (
    Column, Integer, String, DateTime,
    relationship, Base, get_current_utc_time
)



class Category(Base):
    """
    文章分类模型
    对应数据库表：categories
    
    字段说明：
    - id: 主键ID，自动生成
    - name: 分类名称（唯一、索引、非空）
    - description: 分类描述（可选）
    - created_at: 创建时间（默认当前UTC时间）
    
    关联关系：
    - articles: 关联该分类下的所有文章（一对多）
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    
    # 关联文章（字符串引用避免循环依赖）
    articles = relationship("Article", back_populates="category")



__all__ = ["Category"]