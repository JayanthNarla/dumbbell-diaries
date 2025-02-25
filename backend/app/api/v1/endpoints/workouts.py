from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workout import Workout, WorkoutCreate, WorkoutUpdate, WorkoutWithUserInfo
from app.agents.workout_planner import WorkoutRecommendationRequest, WorkoutPlan, generate_workout_plan


router = APIRouter()


# Mock database functions - would be replaced with actual MongoDB operations
async def create_workout_db(workout: WorkoutCreate, user_id: str) -> Workout:
    """Create a workout in the database."""
    # This would be replaced with actual DB call
    workout_id = str(ObjectId())
    return Workout(
        id=workout_id,
        user_id=user_id,
        **workout.dict(),
        created_at=None,
        date=None,
        is_public=False,
        likes_count=0,
        comments_count=0
    )


async def get_workout_by_id_db(workout_id: str) -> Optional[Workout]:
    """Get a workout by ID from the database."""
    # This would be replaced with actual DB call
    return None


async def update_workout_db(workout_id: str, workout_update: WorkoutUpdate) -> Optional[Workout]:
    """Update a workout in the database."""
    # This would be replaced with actual DB call
    return None


async def delete_workout_db(workout_id: str) -> bool:
    """Delete a workout from the database."""
    # This would be replaced with actual DB call
    return True


async def get_user_workouts_db(user_id: str, skip: int = 0, limit: int = 100) -> List[Workout]:
    """Get a user's workouts from the database."""
    # This would be replaced with actual DB call
    return []


async def get_public_workouts_db(skip: int = 0, limit: int = 100) -> List[WorkoutWithUserInfo]:
    """Get public workouts from the database."""
    # This would be replaced with actual DB call
    return []


@router.post("/", response_model=Workout)
async def create_workout(
    workout: WorkoutCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new workout.
    
    Args:
        workout: Workout data
        current_user: Current authenticated user
        
    Returns:
        Created workout
    """
    return await create_workout_db(workout, str(current_user.id))


@router.get("/{workout_id}", response_model=Workout)
async def read_workout(
    workout_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a workout by ID.
    
    Args:
        workout_id: Workout ID
        current_user: Current authenticated user
        
    Returns:
        Workout
    """
    workout = await get_workout_by_id_db(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if workout.user_id != str(current_user.id) and not workout.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return workout


@router.put("/{workout_id}", response_model=Workout)
async def update_workout(
    workout_id: str,
    workout_update: WorkoutUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a workout.
    
    Args:
        workout_id: Workout ID
        workout_update: Workout update data
        current_user: Current authenticated user
        
    Returns:
        Updated workout
    """
    workout = await get_workout_by_id_db(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if workout.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    updated_workout = await update_workout_db(workout_id, workout_update)
    return updated_workout


@router.delete("/{workout_id}", response_model=bool)
async def delete_workout(
    workout_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a workout.
    
    Args:
        workout_id: Workout ID
        current_user: Current authenticated user
        
    Returns:
        True if workout was deleted
    """
    workout = await get_workout_by_id_db(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if workout.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_workout_db(workout_id)
    return result


@router.get("/user/me", response_model=List[Workout])
async def read_user_workouts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's workouts.
    
    Args:
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        current_user: Current authenticated user
        
    Returns:
        List of workouts
    """
    return await get_user_workouts_db(str(current_user.id), skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[Workout])
async def read_user_workouts_by_id(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a user's workouts.
    
    Args:
        user_id: User ID
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        current_user: Current authenticated user
        
    Returns:
        List of workouts
    """
    # In a real implementation, we would check if the current user follows the requested user
    # or if the workouts are public
    return await get_user_workouts_db(user_id, skip=skip, limit=limit)


@router.get("/public", response_model=List[WorkoutWithUserInfo])
async def read_public_workouts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get public workouts.
    
    Args:
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        current_user: Current authenticated user
        
    Returns:
        List of workouts with user info
    """
    return await get_public_workouts_db(skip=skip, limit=limit)


@router.post("/recommendations", response_model=WorkoutPlan)
async def get_workout_recommendations(
    request: WorkoutRecommendationRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get workout recommendations based on the user's goals and preferences.
    
    Args:
        request: Workout recommendation request
        current_user: Current authenticated user
        
    Returns:
        Workout plan recommendations
    """
    # Set the user ID in the request
    request.user_id = str(current_user.id)
    
    # Generate workout plan using LangGraph agent
    try:
        workout_plan = await generate_workout_plan(request)
        return workout_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate workout plan: {str(e)}",
        )
