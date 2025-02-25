from typing import Dict, List, Any, Optional
from datetime import datetime
from bson import ObjectId
import json

from app.db.elasticsearch.indices import (
    WORKOUT_INDEX,
    USER_INDEX,
    FOOD_LOG_INDEX,
    MEASUREMENT_INDEX,
    GOAL_INDEX,
    SOCIAL_POST_INDEX,
    index_document,
    update_document,
    delete_document,
    bulk_index_documents
)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB objects like ObjectId and datetime."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def prepare_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a MongoDB document for Elasticsearch indexing.
    
    Args:
        document: MongoDB document
        
    Returns:
        Document prepared for Elasticsearch
    """
    # Convert MongoDB document to JSON and back to handle ObjectId, datetime, etc.
    json_str = json.dumps(document, cls=JSONEncoder)
    es_doc = json.loads(json_str)
    
    # Replace _id with id for Elasticsearch
    if "_id" in es_doc:
        es_doc["id"] = es_doc.pop("_id")
    
    return es_doc


async def sync_workout(workout: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a workout document to Elasticsearch.
    
    Args:
        workout: Workout document
        operation: Operation type (index, update, delete)
    """
    if not workout:
        return
    
    doc_id = str(workout.get("_id", workout.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(WORKOUT_INDEX, doc_id)
    else:
        es_doc = prepare_document(workout)
        
        # Add additional fields or transformations if needed
        if "likes" in es_doc and isinstance(es_doc["likes"], list):
            es_doc["likes_count"] = len(es_doc["likes"])
        
        if "comments" in es_doc and isinstance(es_doc["comments"], list):
            es_doc["comments_count"] = len(es_doc["comments"])
            
        if operation == "update":
            await update_document(WORKOUT_INDEX, doc_id, es_doc)
        else:
            await index_document(WORKOUT_INDEX, doc_id, es_doc)


async def sync_user(user: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a user document to Elasticsearch.
    
    Args:
        user: User document
        operation: Operation type (index, update, delete)
    """
    if not user:
        return
    
    doc_id = str(user.get("_id", user.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(USER_INDEX, doc_id)
    else:
        es_doc = prepare_document(user)
        
        # Add additional fields or transformations if needed
        if "following" in es_doc and isinstance(es_doc["following"], list):
            es_doc["following_count"] = len(es_doc["following"])
        
        if "followers" in es_doc and isinstance(es_doc["followers"], list):
            es_doc["followers_count"] = len(es_doc["followers"])
            
        # Remove sensitive information
        if "hashed_password" in es_doc:
            del es_doc["hashed_password"]
            
        if operation == "update":
            await update_document(USER_INDEX, doc_id, es_doc)
        else:
            await index_document(USER_INDEX, doc_id, es_doc)


async def sync_food_log(food_log: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a food log document to Elasticsearch.
    
    Args:
        food_log: Food log document
        operation: Operation type (index, update, delete)
    """
    if not food_log:
        return
    
    doc_id = str(food_log.get("_id", food_log.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(FOOD_LOG_INDEX, doc_id)
    else:
        es_doc = prepare_document(food_log)
            
        if operation == "update":
            await update_document(FOOD_LOG_INDEX, doc_id, es_doc)
        else:
            await index_document(FOOD_LOG_INDEX, doc_id, es_doc)


async def sync_measurement(measurement: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a measurement document to Elasticsearch.
    
    Args:
        measurement: Measurement document
        operation: Operation type (index, update, delete)
    """
    if not measurement:
        return
    
    doc_id = str(measurement.get("_id", measurement.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(MEASUREMENT_INDEX, doc_id)
    else:
        es_doc = prepare_document(measurement)
            
        if operation == "update":
            await update_document(MEASUREMENT_INDEX, doc_id, es_doc)
        else:
            await index_document(MEASUREMENT_INDEX, doc_id, es_doc)


async def sync_goal(goal: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a goal document to Elasticsearch.
    
    Args:
        goal: Goal document
        operation: Operation type (index, update, delete)
    """
    if not goal:
        return
    
    doc_id = str(goal.get("_id", goal.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(GOAL_INDEX, doc_id)
    else:
        es_doc = prepare_document(goal)
            
        if operation == "update":
            await update_document(GOAL_INDEX, doc_id, es_doc)
        else:
            await index_document(GOAL_INDEX, doc_id, es_doc)


async def sync_social_post(post: Dict[str, Any], operation: str = "index") -> None:
    """
    Sync a social post document to Elasticsearch.
    
    Args:
        post: Social post document
        operation: Operation type (index, update, delete)
    """
    if not post:
        return
    
    doc_id = str(post.get("_id", post.get("id")))
    if not doc_id:
        return
    
    if operation == "delete":
        await delete_document(SOCIAL_POST_INDEX, doc_id)
    else:
        es_doc = prepare_document(post)
        
        # Add additional fields or transformations if needed
        if "likes" in es_doc and isinstance(es_doc["likes"], list):
            es_doc["likes_count"] = len(es_doc["likes"])
        
        if "comments" in es_doc and isinstance(es_doc["comments"], list):
            es_doc["comments_count"] = len(es_doc["comments"])
            
        if operation == "update":
            await update_document(SOCIAL_POST_INDEX, doc_id, es_doc)
        else:
            await index_document(SOCIAL_POST_INDEX, doc_id, es_doc)
async def sync_post() -> Dict[str, int]:
    return 


async def sync_all_data() -> Dict[str, int]:
    """
    Sync all data from MongoDB to Elasticsearch.
    This is typically used for initial indexing or full reindexing.
    
    Returns:
        Dictionary with count of documents indexed for each entity type
    """
    from app.db.mongodb.mongodb import get_database
    
    db = await get_database()
    counts = {}
    
    # Sync users
    users = []
    async for user in db.users.find():
        es_user = prepare_document(user)
        # Remove sensitive information
        if "hashed_password" in es_user:
            del es_user["hashed_password"]
        # Add document ID
        es_user["_id"] = str(user["_id"])
        users.append(es_user)
    
    await bulk_index_documents(USER_INDEX, users)
    counts["users"] = len(users)
    
    # Sync workouts
    workouts = []
    async for workout in db.workouts.find():
        es_workout = prepare_document(workout)
        es_workout["_id"] = str(workout["_id"])
        workouts.append(es_workout)
    
    await bulk_index_documents(WORKOUT_INDEX, workouts)
    counts["workouts"] = len(workouts)
    
    # Sync food logs
    food_logs = []
    async for food_log in db.food_logs.find():
        es_food_log = prepare_document(food_log)
        es_food_log["_id"] = str(food_log["_id"])
        food_logs.append(es_food_log)
    
    await bulk_index_documents(FOOD_LOG_INDEX, food_logs)
    counts["food_logs"] = len(food_logs)
    
    # Sync measurements
    measurements = []
    async for measurement in db.measurements.find():
        es_measurement = prepare_document(measurement)
        es_measurement["_id"] = str(measurement["_id"])
        measurements.append(es_measurement)
    
    await bulk_index_documents(MEASUREMENT_INDEX, measurements)
    counts["measurements"] = len(measurements)
    
    # Sync goals
    goals = []
    async for goal in db.goals.find():
        es_goal = prepare_document(goal)
        es_goal["_id"] = str(goal["_id"])
        goals.append(es_goal)
    
    await bulk_index_documents(GOAL_INDEX, goals)
    counts["goals"] = len(goals)
    
    # Sync social posts
    posts = []
    async for post in db.social_posts.find():
        es_post = prepare_document(post)
        es_post["_id"] = str(post["_id"])
        posts.append(es_post)
    
    await bulk_index_documents(SOCIAL_POST_INDEX, posts)
    counts["social_posts"] = len(posts)
    
    return counts 