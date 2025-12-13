# app/schemas/messages.py

from imports import BaseModel, Field, EmailStr, datetime
from .minimal import UserMinimal



class MessageBase(BaseModel):
    """私信基础模型（按邮箱发送）"""
    content: str = Field(..., min_length=1, max_length=1000, description="私信内容（1-1000字符）")
    receiver_email: EmailStr = Field(..., description="接收者邮箱")



class MessageCreate(MessageBase):
    """创建私信请求模型"""
    pass



class Message(BaseModel):
    """私信响应模型（补充发送者信息）"""
    id: int = Field(..., description="私信ID")
    sender_id: int = Field(..., description="发送者ID")
    sender_email: EmailStr = Field(..., description="发送者邮箱")
    created_at: datetime = Field(..., description="创建时间戳")
    is_read: bool = Field(False, description="是否已读")
    
    class Config:
        from_attributes = True



class MessageDetail(BaseModel):
    """包含用户信息的私信详情模型"""
    id: int = Field(..., description="私信ID")
    content: str = Field(..., description="私信内容（1-1000字符）")
    created_at: datetime = Field(..., description="创建时间戳")
    is_read: bool = Field(False, description="是否已读")
    sender: UserMinimal = Field(..., description="发送者信息")
    receiver: UserMinimal = Field(..., description="接收者信息")



__all__ = ["MessageBase", "MessageCreate", "Message", "MessageDetail"]