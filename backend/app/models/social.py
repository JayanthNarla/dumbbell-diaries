from datetime import datetime
from pydantic import BaseModel, ConfigDict
from bson import ObjectId
from typing import List, Optional

class PostBase(BaseModel):
    content: str
    media_urls: List[str] = []

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostInDB(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    likes: List[str] = []
    comments_count: int = 0
    likes_count: int = 0

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentInDB(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    post_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    likes: List[str] = []
    likes_count: int = 0 