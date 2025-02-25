from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId


class Exercise(BaseModel):
    """Exercise model for a workout"""
    name: str
    sets: int
    reps: Optional[int] = None
    duration: Optional[int] = None  # in seconds
    weight: Optional[float] = None  # in kg
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


class WorkoutBase(BaseModel):
    """Base workout model"""
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    calories_burned: Optional[int] = None
    exercises: List[Exercise]
    
    class Config:
        populate_by_name = True


class WorkoutCreate(WorkoutBase):
    """Workout creation model"""
    pass


class WorkoutUpdate(BaseModel):
    """Workout update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    calories_burned: Optional[int] = None
    exercises: Optional[List[Exercise]] = None


class WorkoutInDB(WorkoutBase):
    """Workout model as stored in the database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    date: datetime  # The date of the workout (can be different from created_at)
    is_public: bool = False
    likes: List[PyObjectId] = []
    comments: List[Dict[str, Any]] = []  # This could be a reference to a comments collection
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class Workout(WorkoutBase):
    """Workout model returned to clients"""
    id: str
    user_id: str
    created_at: datetime
    date: datetime
    is_public: bool
    likes_count: int = 0
    comments_count: int = 0
    
    class Config:
        orm_mode = True


class WorkoutWithUserInfo(Workout):
    """Workout model with basic user info (for social feed)"""
    user_name: str
    user_profile_picture: Optional[str] = None
