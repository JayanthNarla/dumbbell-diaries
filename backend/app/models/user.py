from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None
    username: str
    
    class Config:
        populate_by_name = True


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


class UserInDB(UserBase):
    """User model as stored in the database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    following: List[PyObjectId] = []
    followers: List[PyObjectId] = []
    
    class Config:
        json_encoders = {
            ObjectId: str
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
    
    class Config:
        orm_mode = True


class UserWithToken(User):
    """User model with access token"""
    access_token: str
    token_type: str = "bearer"
