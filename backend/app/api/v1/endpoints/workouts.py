<<<<<<< Updated upstream
=======
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workout import Workout, WorkoutCreate, WorkoutUpdate, WorkoutWithUserInfo
from app.agents.workout_planner import WorkoutRecommendationRequest, WorkoutPlan, generate_workout_plan
from app.db.mongodb.workouts import (
    create_workout,
    get_workout_by_id,
    update_workout,
    delete_workout,
    get_user_workouts,
    get_public_workouts,
    like_workout as like_workout_db,
    unlike_workout as unlike_workout_db,
    add_comment_to_workout,
    get_workout_comments
)


router = APIRouter()


@router.post("/", response_model=Workout)
async def create_workout_endpoint(
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
    return await create_workout(workout, str(current_user.id))


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
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if str(workout.user_id) != str(current_user.id) and not workout.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return workout


@router.put("/{workout_id}", response_model=Workout)
async def update_workout_endpoint(
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
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if str(workout.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    updated_workout = await update_workout(workout_id, workout_update)
    return updated_workout


@router.delete("/{workout_id}", response_model=bool)
async def delete_workout_endpoint(
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
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    # Check if the workout belongs to the current user
    if str(workout.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_workout(workout_id)
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
    return await get_user_workouts(str(current_user.id), skip=skip, limit=limit)


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
    return await get_user_workouts(user_id, skip=skip, limit=limit)


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
    return await get_public_workouts(skip=skip, limit=limit)


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


@router.post("/{workout_id}/like", response_model=Workout)
async def like_workout_endpoint(
    workout_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Like a workout.
    
    Args:
        workout_id: Workout ID
        current_user: Current authenticated user
        
    Returns:
        Updated workout
    """
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    result = await like_workout_db(workout_id, str(current_user.id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not like workout",
        )
    
    return await get_workout_by_id(workout_id)


@router.post("/{workout_id}/unlike", response_model=Workout)
async def unlike_workout_endpoint(
    workout_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unlike a workout.
    
    Args:
        workout_id: Workout ID
        current_user: Current authenticated user
        
    Returns:
        Updated workout
    """
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    result = await unlike_workout_db(workout_id, str(current_user.id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not unlike workout",
        )
    
    return await get_workout_by_id(workout_id)


@router.post("/{workout_id}/comments", response_model=dict)
async def add_comment(
    workout_id: str,
    content: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a comment to a workout.
    
    Args:
        workout_id: Workout ID
        content: Comment content
        current_user: Current authenticated user
        
    Returns:
        Added comment
    """
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    comment = await add_comment_to_workout(workout_id, str(current_user.id), content)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add comment",
        )
    
    return comment


@router.get("/{workout_id}/comments", response_model=List[dict])
async def get_comments_endpoint(
    workout_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get comments for a workout.
    
    Args:
        workout_id: Workout ID
        current_user: Current authenticated user
        
    Returns:
        List of comments
    """
    workout = await get_workout_by_id(workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )
    
    return await get_workout_comments(workout_id)
>>>>>>> Stashed changes
