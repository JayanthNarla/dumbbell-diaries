from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from bson import ObjectId
from app.models.user import PyObjectId
from enum import Enum


class GoalType(str, Enum):
    """Enum for goal types"""
    WEIGHT = "weight"
    BODY_FAT = "body_fat"
    MEASUREMENT = "measurement"
    WORKOUT = "workout"
    NUTRITION = "nutrition"
    CUSTOM = "custom"


class GoalStatus(str, Enum):
    """Enum for goal status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GoalBase(BaseModel):
    """Base goal model"""
    title: str
    description: Optional[str] = None
    goal_type: GoalType
    target_value: Optional[float] = None  # For numeric goals like weight
    target_date: date
    start_value: Optional[float] = None  # Starting point for numeric goals
    status: GoalStatus = GoalStatus.NOT_STARTED
    custom_data: Optional[Dict[str, Any]] = None  # For complex goals
    
    class Config:
        populate_by_name = True


class GoalCreate(GoalBase):
    """Goal creation model"""
    pass


class GoalUpdate(BaseModel):
    """Goal update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_date: Optional[date] = None
    current_value: Optional[float] = None
    status: Optional[GoalStatus] = None
    custom_data: Optional[Dict[str, Any]] = None


class GoalInDB(GoalBase):
    """Goal model as stored in the database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    current_value: Optional[float] = None
    progress_history: List[Dict[str, Union[datetime, float]]] = []  # Track progress over time
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class Goal(GoalBase):
    """Goal model returned to clients"""
    id: str
    user_id: str
    created_at: datetime
    current_value: Optional[float] = None
    progress_percentage: Optional[float] = None  # Calculated field
    days_remaining: Optional[int] = None  # Calculated field
    
    class Config:
        orm_mode = True


class GoalWithRecommendations(Goal):
    """Goal model with agent recommendations"""
    recommendations: Optional[List[Dict[str, Any]]] = None  # Recommendations from agents
