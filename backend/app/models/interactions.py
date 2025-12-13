# app/models/interactions.py

"""互动模型：管理用户对文章的点赞、收藏行为"""
from .base import (
    Column, Integer, DateTime, ForeignKey, UniqueConstraint,
    relationship, Base, get_current_utc_time
)



class Like(Base):
    """
    文章点赞模型
    对应数据库表：likes
    
    字段说明：
    - id: 主键ID，自动生成
    - user_id: 用户ID（外键关联users表）
    - article_id: 文章ID（外键关联articles表）
    - created_at: 点赞时间（默认当前UTC时间）
    
    约束：
    - (user_id, article_id) 组合唯一，避免重复点赞
    """
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'article_id', name='uix_user_article_like'),
    )

    # 关联关系
    user = relationship("User", backref="likes")
    article = relationship("Article", backref="likes")



class Collect(Base):
    """
    文章收藏模型
    对应数据库表：collects
    
    字段说明：
    - id: 主键ID，自动生成
    - user_id: 用户ID（外键关联users表）
    - article_id: 文章ID（外键关联articles表）
    - created_at: 收藏时间（默认当前UTC时间）
    
    约束：
    - (user_id, article_id) 组合唯一，避免重复收藏
    """
    __tablename__ = "collects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'article_id', name='uix_user_article_collect'),
    )

    # 关联关系
    user = relationship("User", backref="collects")
    article = relationship("Article", backref="collects")



__all__ = ["Like", "Collect"]