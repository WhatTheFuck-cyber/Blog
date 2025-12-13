# app/models/comments.py

"""评论数据模型：存储文章的评论、回复信息"""
from .base import (
    Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint,
    relationship, Base, get_current_utc_time
)



class Comment(Base):
    """
    评论数据模型
    对应数据库表：comments
    
    字段说明：
    - id: 主键ID，自动生成
    - user_id: 评论者ID（外键关联users表）
    - user_name: 评论者名（冗余存储）
    - created_at: 创建时间（默认当前UTC时间）
    - content: 评论内容（非空）
    - article_id: 关联文章ID（外键关联articles表）
    - parent_id: 父评论ID（外键关联comments表，可选，用于回复）
    
    约束：
    - (user_id, created_at) 组合唯一，避免重复评论
    
    关联关系：
    - user: 关联评论者（多对一）
    - article: 关联所属文章（多对一）
    """
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    content = Column(Text, nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'created_at', name='uix_user_time'),
    )

    # 关联关系
    user = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")



__all__ = ["Comment"]