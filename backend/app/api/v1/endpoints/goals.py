<<<<<<< HEAD
<<<<<<< Updated upstream
=======
=======
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from datetime import datetime, date

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.goal import Goal, GoalCreate, GoalUpdate, GoalStatus, GoalType, GoalWithRecommendations
<<<<<<< HEAD
from app.db.mongodb.goals import (
    create_goal,
    get_goal_by_id,
    update_goal,
    delete_goal,
    get_user_goals,
    update_goal_progress,
    get_user_goal_summary
)
=======
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec


router = APIRouter()


<<<<<<< HEAD
@router.post("/", response_model=Goal)
async def create_goal_endpoint(
=======
# Mock database functions - would be replaced with actual MongoDB operations
async def create_goal_db(goal: GoalCreate, user_id: str) -> Goal:
    """Create a goal in the database."""
    # This would be replaced with actual DB call
    goal_id = str(ObjectId())
    return Goal(
        id=goal_id,
        user_id=user_id,
        **goal.dict(),
        created_at=datetime.utcnow(),
        current_value=goal.start_value,
        progress_percentage=0.0,
        days_remaining=(goal.target_date - date.today()).days
    )


async def get_goal_by_id_db(goal_id: str) -> Optional[Goal]:
    """Get a goal by ID from the database."""
    # This would be replaced with actual DB call
    return None


async def update_goal_db(goal_id: str, goal_update: GoalUpdate) -> Optional[Goal]:
    """Update a goal in the database."""
    # This would be replaced with actual DB call
    return None


async def delete_goal_db(goal_id: str) -> bool:
    """Delete a goal from the database."""
    # This would be replaced with actual DB call
    return True


async def get_user_goals_db(
    user_id: str, 
    status: Optional[GoalStatus] = None, 
    goal_type: Optional[GoalType] = None, 
    skip: int = 0, 
    limit: int = 100
) -> List[Goal]:
    """Get a user's goals from the database with filters."""
    # This would be replaced with actual DB call
    return []


async def update_goal_progress_db(goal_id: str, current_value: float) -> Optional[Goal]:
    """Update a goal's progress."""
    # This would be replaced with actual DB call
    return None


async def get_goal_recommendations_db(goal_id: str) -> Optional[GoalWithRecommendations]:
    """Get recommendations for a goal using LangGraph agents."""
    # This would be a more complex implementation involving the agents
    return None


@router.post("/", response_model=Goal)
async def create_goal(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    goal: GoalCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new fitness goal.
    
    Args:
        goal: Goal data
        current_user: Current authenticated user
        
    Returns:
        Created goal
    """
<<<<<<< HEAD
    return await create_goal(goal, str(current_user.id))
=======
    return await create_goal_db(goal, str(current_user.id))
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec


@router.get("/{goal_id}", response_model=Goal)
async def read_goal(
    goal_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a goal by ID.
    
    Args:
        goal_id: Goal ID
        current_user: Current authenticated user
        
    Returns:
        Goal
    """
<<<<<<< HEAD
    goal = await get_goal_by_id(goal_id)
=======
    goal = await get_goal_by_id_db(goal_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
<<<<<<< HEAD
    if str(goal.user_id) != str(current_user.id):
=======
    if goal.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return goal


@router.put("/{goal_id}", response_model=Goal)
<<<<<<< HEAD
async def update_goal_endpoint(
=======
async def update_goal(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    goal_id: str,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a goal.
    
    Args:
        goal_id: Goal ID
        goal_update: Goal update data
        current_user: Current authenticated user
        
    Returns:
        Updated goal
    """
<<<<<<< HEAD
    goal = await get_goal_by_id(goal_id)
=======
    goal = await get_goal_by_id_db(goal_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
<<<<<<< HEAD
    if str(goal.user_id) != str(current_user.id):
=======
    if goal.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
<<<<<<< HEAD
    updated_goal = await update_goal(goal_id, goal_update)
=======
    updated_goal = await update_goal_db(goal_id, goal_update)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    return updated_goal


@router.delete("/{goal_id}", response_model=bool)
<<<<<<< HEAD
async def delete_goal_endpoint(
=======
async def delete_goal(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    goal_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a goal.
    
    Args:
        goal_id: Goal ID
        current_user: Current authenticated user
        
    Returns:
        True if goal was deleted
    """
<<<<<<< HEAD
    goal = await get_goal_by_id(goal_id)
=======
    goal = await get_goal_by_id_db(goal_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
<<<<<<< HEAD
    if str(goal.user_id) != str(current_user.id):
=======
    if goal.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
<<<<<<< HEAD
    result = await delete_goal(goal_id)
=======
    result = await delete_goal_db(goal_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    return result


@router.get("/", response_model=List[Goal])
async def read_user_goals(
    status: Optional[GoalStatus] = None,
    goal_type: Optional[GoalType] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's goals with optional filters.
    
    Args:
        status: Optional goal status filter
        goal_type: Optional goal type filter
        skip: Number of goals to skip
        limit: Maximum number of goals to return
        current_user: Current authenticated user
        
    Returns:
        List of goals
    """
<<<<<<< HEAD
    return await get_user_goals(str(current_user.id), status, goal_type, skip=skip, limit=limit)


@router.put("/{goal_id}/progress", response_model=Goal)
async def update_goal_progress_endpoint(
=======
    return await get_user_goals_db(str(current_user.id), status, goal_type, skip=skip, limit=limit)


@router.put("/{goal_id}/progress", response_model=Goal)
async def update_goal_progress(
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    goal_id: str,
    current_value: float,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a goal's progress.
    
    Args:
        goal_id: Goal ID
        current_value: Current value of the goal metric
        current_user: Current authenticated user
        
    Returns:
        Updated goal
    """
<<<<<<< HEAD
    goal = await get_goal_by_id(goal_id)
=======
    goal = await get_goal_by_id_db(goal_id)
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
<<<<<<< HEAD
    if str(goal.user_id) != str(current_user.id):
=======
    if goal.user_id != str(current_user.id):
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
<<<<<<< HEAD
    updated_goal = await update_goal_progress(goal_id, current_value)
    return updated_goal


@router.get("/summary", response_model=Dict[str, Any])
async def get_user_goal_summary_endpoint(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a summary of the user's goals.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Goal summary with counts by status and type
    """
    return await get_user_goal_summary(str(current_user.id))
>>>>>>> Stashed changes
=======
    updated_goal = await update_goal_progress_db(goal_id, current_value)
    return updated_goal


@router.get("/{goal_id}/recommendations", response_model=GoalWithRecommendations)
async def get_goal_recommendations(
    goal_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get recommendations for achieving a goal.
    
    Args:
        goal_id: Goal ID
        current_user: Current authenticated user
        
    Returns:
        Goal with recommendations
    """
    goal = await get_goal_by_id_db(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
    if goal.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    goal_with_recommendations = await get_goal_recommendations_db(goal_id)
    if not goal_with_recommendations:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations for this goal",
        )
    
    return goal_with_recommendations
>>>>>>> 2d5688bfff6c12d6a7862ab2fa1a8d3da8aab2ec
