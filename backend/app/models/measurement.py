from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId


class MeasurementBase(BaseModel):
    """Base measurement model"""
    date: datetime
    weight: Optional[float] = None  # in kg
    height: Optional[float] = None  # in cm
    body_fat: Optional[float] = None  # percentage
    chest: Optional[float] = None  # in cm
    waist: Optional[float] = None  # in cm
    hips: Optional[float] = None  # in cm
    arms: Optional[Dict[str, float]] = None  # left and right in cm
    legs: Optional[Dict[str, float]] = None  # left and right in cm
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = None  # URLs to progress photos
    
    class Config:
        populate_by_name = True


class MeasurementCreate(MeasurementBase):
    """Measurement creation model"""
    pass


class MeasurementUpdate(BaseModel):
    """Measurement update model"""
    date: Optional[datetime] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    body_fat: Optional[float] = None
    chest: Optional[float] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    arms: Optional[Dict[str, float]] = None
    legs: Optional[Dict[str, float]] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = None


class MeasurementInDB(MeasurementBase):
    """Measurement model as stored in the database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class Measurement(MeasurementBase):
    """Measurement model returned to clients"""
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True


class MeasurementHistory(BaseModel):
    """Model for returning measurement history/trends"""
    dates: List[datetime]
    weights: Optional[List[float]] = None
    body_fat: Optional[List[float]] = None
    measurements: Optional[Dict[str, List[float]]] = None  # Different measurement types
