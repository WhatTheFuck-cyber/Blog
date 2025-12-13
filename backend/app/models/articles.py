# app/models/articles.py

"""文章数据模型：存储文章内容、作者、分类等信息"""
from .base import (
    Column, Integer, String, DateTime, Text, ForeignKey,
    relationship, Base, get_current_utc_time
)



class Article(Base):
    """
    文章数据模型
    对应数据库表：articles
    
    字段说明：
    - id: 主键ID，自动生成
    - title: 文章标题（索引）
    - created_at: 创建时间（默认当前UTC时间）
    - content: 文章内容（长文本）
    - owner_id: 作者ID（外键关联users表）
    - owner_name: 作者名（冗余存储，避免联表查询）
    - category_id: 分类ID（外键关联categories表，可选）
    
    关联关系：
    - owner: 关联文章作者（多对一）
    - comments: 关联文章的所有评论（一对多，删除文章时级联删除评论）
    - category: 关联文章所属分类（多对一）
    - likes: 关联文章的所有点赞（一对多）
    - collects: 关联文章的所有收藏（一对多）
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # 关联关系（字符串引用避免循环依赖）
    owner = relationship("User", back_populates="articles")
    comments = relationship(
        "Comment", 
        back_populates="article", 
        cascade="all, delete-orphan", 
        passive_deletes=True
    )
    category = relationship("Category", back_populates="articles")



__all__ = ["Article"]