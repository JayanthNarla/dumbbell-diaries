from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId


class FoodItem(BaseModel):
    """Food item model"""
    name: str
    serving_size: float
    serving_unit: str  # e.g., grams, cups, pieces
    calories: int
    protein: Optional[float] = None  # in grams
    carbs: Optional[float] = None  # in grams
    fat: Optional[float] = None  # in grams
    fiber: Optional[float] = None  # in grams
    sugar: Optional[float] = None  # in grams
    sodium: Optional[float] = None  # in mg
    
    class Config:
        populate_by_name = True


class MealBase(BaseModel):
    """Base meal model"""
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[Dict[str, Any]]  # List of food items with quantity
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


class MealCreate(MealBase):
    """Meal creation model"""
    pass


class MealUpdate(BaseModel):
    """Meal update model"""
    meal_type: Optional[str] = None
    foods: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class FoodLogBase(BaseModel):
    """Base food log model for a day"""
    date: datetime
    meals: List[MealBase]
    total_calories: Optional[int] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    water_intake: Optional[int] = None  # in milliliters
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


class FoodLogCreate(FoodLogBase):
    """Food log creation model"""
    pass


class FoodLogUpdate(BaseModel):
    """Food log update model"""
    meals: Optional[List[MealBase]] = None
    total_calories: Optional[int] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    water_intake: Optional[int] = None
    notes: Optional[str] = None


class FoodLogInDB(FoodLogBase):
    """Food log model as stored in the database"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str
        }


class FoodLog(FoodLogBase):
    """Food log model returned to clients"""
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True
