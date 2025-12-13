# app/models/users.py

"""用户数据模型：存储用户基础信息、账号状态等"""
from .base import (
    Column, Integer, String, DateTime, Boolean,
    relationship, Base
)



class User(Base):
    """
    用户数据模型
    对应数据库表：users
    
    字段说明：
    - id: 主键ID，自动生成
    - username: 用户名（唯一、索引）
    - email: 邮箱地址（唯一、索引，可选）
    - hashed_password: 密码哈希值（不可逆）
    - is_active: 用户状态（True=可用，False=服务器归属/注销）
    - deactivated_at: 注销时间戳（可选）
    
    关联关系：
    - articles: 关联用户发布的所有文章（一对多）
    - comments: 关联用户发布的所有评论（一对多）
    - sent_messages: 关联用户发送的私信（一对多）
    - received_messages: 关联用户接收的私信（一对多）
    - likes: 关联用户点赞的文章（一对多）
    - collects: 关联用户收藏的文章（一对多）
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    activate_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)

    # 关联关系（使用字符串引用避免循环导入）
    articles = relationship("Article", back_populates="owner")
    comments = relationship("Comment", back_populates="user")



__all__ = ["User"]