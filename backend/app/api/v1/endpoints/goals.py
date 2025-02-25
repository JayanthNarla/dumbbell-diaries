<<<<<<< Updated upstream
=======
from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from datetime import datetime, date

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.goal import Goal, GoalCreate, GoalUpdate, GoalStatus, GoalType, GoalWithRecommendations
from app.db.mongodb.goals import (
    create_goal,
    get_goal_by_id,
    update_goal,
    delete_goal,
    get_user_goals,
    update_goal_progress,
    get_user_goal_summary
)


router = APIRouter()


@router.post("/", response_model=Goal)
async def create_goal_endpoint(
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
    return await create_goal(goal, str(current_user.id))


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
    goal = await get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return goal


@router.put("/{goal_id}", response_model=Goal)
async def update_goal_endpoint(
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
    goal = await get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    updated_goal = await update_goal(goal_id, goal_update)
    return updated_goal


@router.delete("/{goal_id}", response_model=bool)
async def delete_goal_endpoint(
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
    goal = await get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_goal(goal_id)
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
    return await get_user_goals(str(current_user.id), status, goal_type, skip=skip, limit=limit)


@router.put("/{goal_id}/progress", response_model=Goal)
async def update_goal_progress_endpoint(
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
    goal = await get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    
    # Check if the goal belongs to the current user
    if str(goal.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
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
