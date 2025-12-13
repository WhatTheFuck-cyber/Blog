# app/schemas/interactions.py

from imports import BaseModel, datetime, Field



# 点赞相关
class LikeBase(BaseModel):
    article_id: int = Field(..., description="点赞的文章ID")



class LikeCreate(LikeBase):
    pass



class Like(LikeBase):
    id: int = Field(..., description="点赞ID")
    user_id: int = Field(..., description="点赞用户ID")
    created_at: datetime = Field(..., description="点赞时间戳")
    
    class Config:
        from_attributes = True



# 收藏相关
class CollectBase(BaseModel):
    article_id: int = Field(..., description="收藏的文章ID")



class CollectCreate(CollectBase):
    pass



class Collect(CollectBase):
    id: int = Field(..., description="收藏ID")
    user_id: int = Field(..., description="收藏用户ID")
    created_at: datetime = Field(..., description="收藏时间戳")
    
    class Config:
        from_attributes = True



__all__ = ["LikeBase", "LikeCreate", "Like",
           "CollectBase", "CollectCreate","Collect"]