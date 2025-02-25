from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.workout import WorkoutCreate, WorkoutUpdate, WorkoutInDB, Workout, WorkoutWithUserInfo
from app.db.mongodb.mongodb import get_database
from app.db.elasticsearch.sync import sync_workout


async def create_workout(workout: WorkoutCreate, user_id: str) -> WorkoutInDB:
    """
    Create a new workout.
    
    Args:
        workout: Workout data
        user_id: User ID
        
    Returns:
        Created workout
    """
    db = await get_database()
    
    workout_in_db = WorkoutInDB(
        **workout.dict(),
        user_id=ObjectId(user_id),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        date=workout.date or datetime.utcnow(),
        is_public=False,
        likes=[],
        comments=[]
    )
    
    result = await db.workouts.insert_one(workout_in_db.dict(by_alias=True))
    workout_in_db.id = result.inserted_id
    
    # Index in Elasticsearch
    await sync_workout(workout_in_db.dict(by_alias=True))
    
    return workout_in_db


async def get_workout_by_id(workout_id: str) -> Optional[WorkoutInDB]:
    """
    Get a workout by ID.
    
    Args:
        workout_id: Workout ID
        
    Returns:
        Workout or None if not found
    """
    db = await get_database()
    
    workout_data = await db.workouts.find_one({"_id": ObjectId(workout_id)})
    if workout_data:
        return WorkoutInDB(**workout_data)
    
    return None


async def update_workout(workout_id: str, workout_update: WorkoutUpdate) -> Optional[WorkoutInDB]:
    """
    Update a workout.
    
    Args:
        workout_id: Workout ID
        workout_update: Workout update data
        
    Returns:
        Updated workout or None if not found
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in workout_update.dict().items() if v is not None}
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the workout
    result = await db.workouts.update_one(
        {"_id": ObjectId(workout_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated workout
        updated_workout = await get_workout_by_id(workout_id)
        
        # Update in Elasticsearch
        if updated_workout:
            await sync_workout(updated_workout.dict(by_alias=True), operation="update")
            
        return updated_workout
    
    return None


async def delete_workout(workout_id: str) -> bool:
    """
    Delete a workout.
    
    Args:
        workout_id: Workout ID
        
    Returns:
        True if workout was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.workouts.delete_one({"_id": ObjectId(workout_id)})
    
    # Delete from Elasticsearch
    if result.deleted_count:
        await sync_workout({"_id": workout_id}, operation="delete")
        
    return result.deleted_count > 0


async def get_user_workouts(
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    sort_by: str = "date",
    sort_direction: int = -1
) -> List[WorkoutInDB]:
    """
    Get a user's workouts with pagination.
    
    Args:
        user_id: User ID
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of workouts
    """
    db = await get_database()
    workouts = []
    
    cursor = db.workouts.find(
        {"user_id": ObjectId(user_id)}
    ).sort(
        sort_by, sort_direction
    ).skip(skip).limit(limit)
    
    async for workout_data in cursor:
        workouts.append(WorkoutInDB(**workout_data))
    
    return workouts


async def get_public_workouts(
    skip: int = 0, 
    limit: int = 100,
    sort_by: str = "created_at",
    sort_direction: int = -1
) -> List[Dict[str, Any]]:
    """
    Get public workouts with user info for the social feed.
    
    Args:
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of workouts with user info
    """
    db = await get_database()
    workouts = []
    
    # Aggregate to get workouts with user info
    pipeline = [
        {"$match": {"is_public": True}},
        {"$sort": {sort_by: sort_direction}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "id": "$_id",
                "user_id": 1,
                "title": 1,
                "description": 1,
                "duration": 1,
                "calories_burned": 1,
                "exercises": 1,
                "date": 1,
                "created_at": 1,
                "is_public": 1,
                "likes_count": {"$size": {"$ifNull": ["$likes", []]}},
                "comments_count": {"$size": {"$ifNull": ["$comments", []]}},
                "user_name": "$user.username",
                "user_profile_picture": "$user.profile_picture"
            }
        }
    ]
    
    cursor = db.workouts.aggregate(pipeline)
    async for workout_data in cursor:
        workout_data["id"] = str(workout_data["id"])
        workout_data["user_id"] = str(workout_data["user_id"])
        workouts.append(workout_data)
    
    return workouts


async def like_workout(workout_id: str, user_id: str) -> bool:
    """
    Like a workout.
    
    Args:
        workout_id: Workout ID
        user_id: User ID who is liking
        
    Returns:
        True if successfully liked, False otherwise
    """
    db = await get_database()
    
    result = await db.workouts.update_one(
        {
            "_id": ObjectId(workout_id),
            "likes": {"$ne": ObjectId(user_id)}
        },
        {"$addToSet": {"likes": ObjectId(user_id)}}
    )
    
    if result.modified_count:
        # Update in Elasticsearch
        workout = await get_workout_by_id(workout_id)
        if workout:
            await sync_workout(workout.dict(by_alias=True), operation="update")
            
    return result.modified_count > 0


async def unlike_workout(workout_id: str, user_id: str) -> bool:
    """
    Unlike a workout.
    
    Args:
        workout_id: Workout ID
        user_id: User ID who is unliking
        
    Returns:
        True if successfully unliked, False otherwise
    """
    db = await get_database()
    
    result = await db.workouts.update_one(
        {"_id": ObjectId(workout_id)},
        {"$pull": {"likes": ObjectId(user_id)}}
    )
    
    if result.modified_count:
        # Update in Elasticsearch
        workout = await get_workout_by_id(workout_id)
        if workout:
            await sync_workout(workout.dict(by_alias=True), operation="update")
            
    return result.modified_count > 0


async def add_comment_to_workout(
    workout_id: str, 
    user_id: str, 
    content: str
) -> Optional[Dict[str, Any]]:
    """
    Add a comment to a workout.
    
    Args:
        workout_id: Workout ID
        user_id: User ID who is commenting
        content: Comment content
        
    Returns:
        Created comment or None if workout not found
    """
    db = await get_database()
    
    comment_id = ObjectId()
    comment = {
        "_id": comment_id,
        "user_id": ObjectId(user_id),
        "content": content,
        "created_at": datetime.utcnow()
    }
    
    result = await db.workouts.update_one(
        {"_id": ObjectId(workout_id)},
        {"$push": {"comments": comment}}
    )
    
    if result.modified_count:
        # Update in Elasticsearch
        workout = await get_workout_by_id(workout_id)
        if workout:
            await sync_workout(workout.dict(by_alias=True), operation="update")
            
        # Return the comment with string IDs
        comment["_id"] = str(comment["_id"])
        comment["user_id"] = str(comment["user_id"])
        return comment
    
    return None


async def get_workout_comments(workout_id: str) -> List[Dict[str, Any]]:
    """
    Get comments for a workout.
    
    Args:
        workout_id: Workout ID
        
    Returns:
        List of comments
    """
    db = await get_database()
    
    # Get the workout with comments
    workout_data = await db.workouts.find_one(
        {"_id": ObjectId(workout_id)},
        {"comments": 1}
    )
    
    if workout_data and "comments" in workout_data:
        # Convert ObjectId to string
        comments = workout_data["comments"]
        for comment in comments:
            comment["_id"] = str(comment["_id"])
            comment["user_id"] = str(comment["user_id"])
        
        return comments
    
    return [] 