from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.mongodb import PyObjectId, MongoBaseModel
from pydantic import ConfigDict


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None
    username: str
    
    class Config:
        populate_by_name = True
        from_attributes=True


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None


class UserInDB(UserBase, MongoBaseModel):
    """User model as stored in the database"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    following: List[PyObjectId] = []
    followers: List[PyObjectId] = []
    
    class Config:
        json_encoders = {
            PyObjectId: str
        }


class User(UserBase):
    """User model returned to clients"""
    id: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    following_count: int = 0
    followers_count: int = 0
    
    model_config = ConfigDict(
        from_attributes=True
    )


class UserWithToken(User):
    """User model with access token"""
    access_token: str
    token_type: str = "bearer"
