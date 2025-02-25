from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.goal import GoalCreate, GoalUpdate, GoalInDB, Goal, GoalStatus, GoalType
from app.db.mongodb.mongodb import get_database
from app.db.elasticsearch.sync import sync_goal


async def create_goal(goal: GoalCreate, user_id: str) -> GoalInDB:
    """
    Create a new fitness goal.
    
    Args:
        goal: Goal data
        user_id: User ID
        
    Returns:
        Created goal
    """
    db = await get_database()
    
    # Calculate days remaining and progress percentage
    days_remaining = None
    progress_percentage = 0.0
    
    if goal.end_date:
        days_remaining = (goal.end_date - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0
    
    if goal.current_value is not None and goal.target_value is not None:
        if goal.goal_type == GoalType.DECREASE:
            initial_diff = goal.start_value - goal.target_value
            current_diff = goal.start_value - goal.current_value
            if initial_diff > 0:
                progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
        else:  # INCREASE or MAINTAIN
            initial_diff = goal.target_value - goal.start_value
            current_diff = goal.current_value - goal.start_value
            if initial_diff > 0:
                progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
    
    # Set status
    status = GoalStatus.IN_PROGRESS
    if progress_percentage >= 100:
        status = GoalStatus.COMPLETED
    elif goal.end_date and goal.end_date < datetime.utcnow():
        status = GoalStatus.EXPIRED
    
    goal_in_db = GoalInDB(
        **goal.dict(),
        user_id=ObjectId(user_id),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_value=goal.current_value or goal.start_value,
        progress_percentage=progress_percentage,
        days_remaining=days_remaining,
        status=status
    )
    
    result = await db.goals.insert_one(goal_in_db.dict(by_alias=True))
    goal_in_db.id = result.inserted_id
    
    # Index in Elasticsearch
    # await sync_goal(goal_in_db.dict(by_alias=True))
    
    return goal_in_db


async def get_goal_by_id(goal_id: str) -> Optional[GoalInDB]:
    """
    Get a goal by ID.
    
    Args:
        goal_id: Goal ID
        
    Returns:
        Goal or None if not found
    """
    db = await get_database()
    
    goal_data = await db.goals.find_one({"_id": ObjectId(goal_id)})
    if goal_data:
        return GoalInDB(**goal_data)
    
    return None


async def update_goal(goal_id: str, goal_update: GoalUpdate) -> Optional[GoalInDB]:
    """
    Update a goal.
    
    Args:
        goal_id: Goal ID
        goal_update: Goal update data
        
    Returns:
        Updated goal or None if not found
    """
    db = await get_database()
    
    # Get current goal
    current_goal = await get_goal_by_id(goal_id)
    if not current_goal:
        return None
    
    # Filter out None values
    update_data = {k: v for k, v in goal_update.dict().items() if v is not None}
    
    # Recalculate days_remaining if end_date is updated
    if "end_date" in update_data:
        end_date = update_data["end_date"]
        days_remaining = (end_date - datetime.utcnow()).days
        if days_remaining < 0:
            days_remaining = 0
        update_data["days_remaining"] = days_remaining
    
    # Recalculate progress_percentage if current_value, target_value, or start_value is updated
    if any(field in update_data for field in ["current_value", "target_value", "start_value"]):
        # Get values, using updated values where available and current values otherwise
        current_value = update_data.get("current_value", current_goal.current_value)
        target_value = update_data.get("target_value", current_goal.target_value)
        start_value = update_data.get("start_value", current_goal.start_value)
        goal_type = update_data.get("goal_type", current_goal.goal_type)
        
        progress_percentage = 0.0
        if current_value is not None and target_value is not None:
            if goal_type == GoalType.DECREASE:
                initial_diff = start_value - target_value
                current_diff = start_value - current_value
                if initial_diff > 0:
                    progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
            else:  # INCREASE or MAINTAIN
                initial_diff = target_value - start_value
                current_diff = current_value - start_value
                if initial_diff > 0:
                    progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
        
        update_data["progress_percentage"] = progress_percentage
    
    # Update status if needed
    if ("progress_percentage" in update_data) or ("end_date" in update_data):
        progress = update_data.get("progress_percentage", current_goal.progress_percentage)
        end_date = update_data.get("end_date", current_goal.end_date)
        
        if progress >= 100:
            update_data["status"] = GoalStatus.COMPLETED
        elif end_date and end_date < datetime.utcnow():
            update_data["status"] = GoalStatus.EXPIRED
        else:
            update_data["status"] = GoalStatus.IN_PROGRESS
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the goal
    result = await db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated goal
        updated_goal = await get_goal_by_id(goal_id)
        
        # Update in Elasticsearch
        # if updated_goal:
        #     await sync_goal(updated_goal.dict(by_alias=True), operation="update")
            
        return updated_goal
    
    return None


async def delete_goal(goal_id: str) -> bool:
    """
    Delete a goal.
    
    Args:
        goal_id: Goal ID
        
    Returns:
        True if goal was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.goals.delete_one({"_id": ObjectId(goal_id)})
    
    # Delete from Elasticsearch
    # if result.deleted_count:
    #     await sync_goal({"_id": goal_id}, operation="delete")
        
    return result.deleted_count > 0


async def get_user_goals(
    user_id: str,
    status: Optional[GoalStatus] = None,
    goal_type: Optional[GoalType] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_direction: int = -1
) -> List[GoalInDB]:
    """
    Get a user's goals with pagination and filters.
    
    Args:
        user_id: User ID
        status: Optional status filter
        goal_type: Optional goal type filter
        skip: Number of goals to skip
        limit: Maximum number of goals to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of goals
    """
    db = await get_database()
    goals = []
    
    # Build query filters
    filters = {"user_id": ObjectId(user_id)}
    
    if status:
        filters["status"] = status
    
    if goal_type:
        filters["goal_type"] = goal_type
    
    cursor = db.goals.find(filters).sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    async for goal_data in cursor:
        goals.append(GoalInDB(**goal_data))
    
    return goals


async def update_goal_progress(goal_id: str, current_value: float) -> Optional[GoalInDB]:
    """
    Update the progress of a goal based on current value.
    
    Args:
        goal_id: Goal ID
        current_value: Current value
        
    Returns:
        Updated goal or None if not found
    """
    db = await get_database()
    
    # Get current goal
    current_goal = await get_goal_by_id(goal_id)
    if not current_goal:
        return None
    
    # Calculate new progress percentage
    progress_percentage = 0.0
    if current_goal.target_value is not None:
        if current_goal.goal_type == GoalType.DECREASE:
            initial_diff = current_goal.start_value - current_goal.target_value
            current_diff = current_goal.start_value - current_value
            if initial_diff > 0:
                progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
        else:  # INCREASE or MAINTAIN
            initial_diff = current_goal.target_value - current_goal.start_value
            current_diff = current_value - current_goal.start_value
            if initial_diff > 0:
                progress_percentage = min(100.0, (current_diff / initial_diff) * 100)
    
    # Determine status
    status = current_goal.status
    if progress_percentage >= 100:
        status = GoalStatus.COMPLETED
    elif current_goal.end_date and current_goal.end_date < datetime.utcnow():
        status = GoalStatus.EXPIRED
    else:
        status = GoalStatus.IN_PROGRESS
    
    # Update the goal
    update_data = {
        "current_value": current_value,
        "progress_percentage": progress_percentage,
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    result = await db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated goal
        updated_goal = await get_goal_by_id(goal_id)
        
        # Update in Elasticsearch
        # if updated_goal:
        #     await sync_goal(updated_goal.dict(by_alias=True), operation="update")
            
        return updated_goal
    
    return None


async def get_user_goal_summary(user_id: str) -> Dict[str, Any]:
    """
    Get a summary of a user's goals.
    
    Args:
        user_id: User ID
        
    Returns:
        Goal summary with statistics
    """
    db = await get_database()
    
    # Aggregate to get summary
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id)
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_progress": {"$avg": "$progress_percentage"}
            }
        }
    ]
    
    result = await db.goals.aggregate(pipeline).to_list(length=None)
    
    # Format the summary
    summary = {
        "total_goals": 0,
        "completed_goals": 0,
        "in_progress_goals": 0,
        "expired_goals": 0,
        "avg_completion_rate": 0
    }
    
    for status_group in result:
        status_name = status_group["_id"]
        count = status_group["count"]
        
        summary["total_goals"] += count
        
        if status_name == GoalStatus.COMPLETED:
            summary["completed_goals"] = count
        elif status_name == GoalStatus.IN_PROGRESS:
            summary["in_progress_goals"] = count
            summary["avg_progress_for_in_progress"] = status_group["avg_progress"]
        elif status_name == GoalStatus.EXPIRED:
            summary["expired_goals"] = count
    
    # Calculate completion rate
    if summary["total_goals"] > 0:
        summary["avg_completion_rate"] = (summary["completed_goals"] / summary["total_goals"]) * 100
    
    return summary 