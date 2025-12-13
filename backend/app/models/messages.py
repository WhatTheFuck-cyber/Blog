# app/models/messages.py

"""私信消息模型：存储用户间的私信沟通记录"""
from .base import (
    Column, Integer, DateTime, Boolean, Text, ForeignKey,
    relationship, Base, get_current_utc_time
)



class Message(Base):
    """
    私信消息模型
    对应数据库表：messages
    
    字段说明：
    - id: 主键ID，自动生成
    - sender_id: 发送者ID（外键关联users表）
    - receiver_id: 接收者ID（外键关联users表）
    - content: 消息内容（非空）
    - created_at: 创建时间（默认当前UTC时间）
    - is_read: 是否已读（默认False）
    
    关联关系：
    - sender: 关联发送者（多对一）
    - receiver: 关联接收者（多对一）
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # 关联发送者和接收者（指定外键避免歧义）
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")



__all__ = ["Message"]