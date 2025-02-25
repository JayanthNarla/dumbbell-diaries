<<<<<<< HEAD
<<<<<<< Updated upstream
=======
from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
=======
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
from bson import ObjectId
from datetime import datetime, date

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.food import FoodLog, FoodLogCreate, FoodLogUpdate, MealBase
from app.agents.meal_planner import MealPlanRequest, MealPlan, generate_meal_plan
<<<<<<< HEAD
from app.db.mongodb.food import (
    create_food_log,
    get_food_log_by_id,
    update_food_log,
    delete_food_log,
    get_user_food_logs,
    add_meal_to_food_log,
    get_nutrition_summary
)
=======
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec


router = APIRouter()


<<<<<<< HEAD
@router.post("/", response_model=FoodLog)
async def create_food_log_endpoint(
=======
# Mock database functions - would be replaced with actual MongoDB operations
async def create_food_log_db(food_log: FoodLogCreate, user_id: str) -> FoodLog:
    """Create a food log in the database."""
    # This would be replaced with actual DB call
    food_log_id = str(ObjectId())
    return FoodLog(
        id=food_log_id,
        user_id=user_id,
        **food_log.dict(),
        created_at=datetime.utcnow()
    )


async def get_food_log_by_id_db(food_log_id: str) -> Optional[FoodLog]:
    """Get a food log by ID from the database."""
    # This would be replaced with actual DB call
    return None


async def update_food_log_db(food_log_id: str, food_log_update: FoodLogUpdate) -> Optional[FoodLog]:
    """Update a food log in the database."""
    # This would be replaced with actual DB call
    return None


async def delete_food_log_db(food_log_id: str) -> bool:
    """Delete a food log from the database."""
    # This would be replaced with actual DB call
    return True


async def get_user_food_logs_db(user_id: str, start_date: date = None, end_date: date = None, skip: int = 0, limit: int = 100) -> List[FoodLog]:
    """Get a user's food logs from the database with date range filter."""
    # This would be replaced with actual DB call
    return []


@router.post("/", response_model=FoodLog)
async def create_food_log(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    food_log: FoodLogCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new food log for tracking meals.
    
    Args:
        food_log: Food log data
        current_user: Current authenticated user
        
    Returns:
        Created food log
    """
<<<<<<< HEAD
    return await create_food_log(food_log, str(current_user.id))
=======
    return await create_food_log_db(food_log, str(current_user.id))
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec


@router.get("/{food_log_id}", response_model=FoodLog)
async def read_food_log(
    food_log_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a food log by ID.
    
    Args:
        food_log_id: Food log ID
        current_user: Current authenticated user
        
    Returns:
        Food log
    """
<<<<<<< HEAD
    food_log = await get_food_log_by_id(food_log_id)
=======
    food_log = await get_food_log_by_id_db(food_log_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )
    
    # Check if the food log belongs to the current user
<<<<<<< HEAD
    if str(food_log.user_id) != str(current_user.id):
=======
    if food_log.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return food_log


@router.put("/{food_log_id}", response_model=FoodLog)
<<<<<<< HEAD
async def update_food_log_endpoint(
=======
async def update_food_log(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    food_log_id: str,
    food_log_update: FoodLogUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a food log.
    
    Args:
        food_log_id: Food log ID
        food_log_update: Food log update data
        current_user: Current authenticated user
        
    Returns:
        Updated food log
    """
<<<<<<< HEAD
    food_log = await get_food_log_by_id(food_log_id)
=======
    food_log = await get_food_log_by_id_db(food_log_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )
    
    # Check if the food log belongs to the current user
<<<<<<< HEAD
    if str(food_log.user_id) != str(current_user.id):
=======
    if food_log.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
<<<<<<< HEAD
    updated_food_log = await update_food_log(food_log_id, food_log_update)
=======
    updated_food_log = await update_food_log_db(food_log_id, food_log_update)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    return updated_food_log


@router.delete("/{food_log_id}", response_model=bool)
<<<<<<< HEAD
async def delete_food_log_endpoint(
=======
async def delete_food_log(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    food_log_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a food log.
    
    Args:
        food_log_id: Food log ID
        current_user: Current authenticated user
        
    Returns:
        True if food log was deleted
    """
<<<<<<< HEAD
    food_log = await get_food_log_by_id(food_log_id)
=======
    food_log = await get_food_log_by_id_db(food_log_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )
    
    # Check if the food log belongs to the current user
<<<<<<< HEAD
    if str(food_log.user_id) != str(current_user.id):
=======
    if food_log.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
<<<<<<< HEAD
    result = await delete_food_log(food_log_id)
=======
    result = await delete_food_log_db(food_log_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    return result


@router.get("/", response_model=List[FoodLog])
async def read_user_food_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's food logs with optional date range filter.
    
    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        skip: Number of logs to skip
        limit: Maximum number of logs to return
        current_user: Current authenticated user
        
    Returns:
        List of food logs
    """
<<<<<<< HEAD
    return await get_user_food_logs(str(current_user.id), start_date, end_date, skip=skip, limit=limit)
=======
    return await get_user_food_logs_db(str(current_user.id), start_date, end_date, skip=skip, limit=limit)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec


@router.post("/meal-plan", response_model=MealPlan)
async def get_meal_recommendations(
    request: MealPlanRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get personalized meal plan recommendations based on user's goals and preferences.
    
    Args:
        request: Meal plan request
        current_user: Current authenticated user
        
    Returns:
        Meal plan recommendations
    """
    # Set the user ID in the request
    request.user_id = str(current_user.id)
    
    # Generate meal plan using LangGraph agent
    try:
        meal_plan = await generate_meal_plan(request)
        return meal_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate meal plan: {str(e)}",
        )


@router.post("/{food_log_id}/meals", response_model=FoodLog)
<<<<<<< HEAD
async def add_meal_to_food_log_endpoint(
=======
async def add_meal_to_food_log(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    food_log_id: str,
    meal: MealBase,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a meal to an existing food log.
    
    Args:
        food_log_id: Food log ID
        meal: Meal to add
        current_user: Current authenticated user
        
    Returns:
        Updated food log
    """
<<<<<<< HEAD
    food_log = await get_food_log_by_id(food_log_id)
=======
    food_log = await get_food_log_by_id_db(food_log_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not food_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log not found",
        )
    
    # Check if the food log belongs to the current user
<<<<<<< HEAD
    if str(food_log.user_id) != str(current_user.id):
=======
    if food_log.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Add the meal to the food log
<<<<<<< HEAD
    updated_food_log = await add_meal_to_food_log(food_log_id, meal)
    return updated_food_log


@router.get("/nutrition-summary", response_model=Dict[str, Any])
async def get_nutrition_summary_endpoint(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get nutrition summary for a date range.
    
    Args:
        start_date: Start date for summary
        end_date: End date for summary
        current_user: Current authenticated user
        
    Returns:
        Nutrition summary
    """
    return await get_nutrition_summary(str(current_user.id), start_date, end_date)
>>>>>>> Stashed changes
=======
    update_data = FoodLogUpdate(
        meals=[*food_log.meals, meal]
    )
    
    updated_food_log = await update_food_log_db(food_log_id, update_data)
    return updated_food_log
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
