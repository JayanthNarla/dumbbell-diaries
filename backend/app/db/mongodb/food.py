from typing import List, Optional, Dict, Any
from datetime import datetime, date
from bson import ObjectId

from app.models.food import FoodLogCreate, FoodLogUpdate, FoodLogInDB, FoodLog, MealBase
from app.db.mongodb.mongodb import get_database
from app.db.elasticsearch.sync import sync_food_log


async def create_food_log(food_log: FoodLogCreate, user_id: str) -> FoodLogInDB:
    """
    Create a new food log.
    
    Args:
        food_log: Food log data
        user_id: User ID
        
    Returns:
        Created food log
    """
    db = await get_database()
    
    # Calculate totals if not provided
    total_calories = food_log.total_calories or 0
    total_protein = food_log.total_protein or 0
    total_carbs = food_log.total_carbs or 0
    total_fat = food_log.total_fat or 0
    
    if not food_log.total_calories and food_log.meals:
        for meal in food_log.meals:
            for food_item in meal.foods:
                if "calories" in food_item:
                    total_calories += food_item["calories"] * food_item.get("quantity", 1)
                if "protein" in food_item:
                    total_protein += food_item["protein"] * food_item.get("quantity", 1)
                if "carbs" in food_item:
                    total_carbs += food_item["carbs"] * food_item.get("quantity", 1)
                if "fat" in food_item:
                    total_fat += food_item["fat"] * food_item.get("quantity", 1)
    
    food_log_in_db = FoodLogInDB(
        **food_log.dict(),
        user_id=ObjectId(user_id),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat
    )
    
    result = await db.food_logs.insert_one(food_log_in_db.dict(by_alias=True))
    food_log_in_db.id = result.inserted_id
    
    # Index in Elasticsearch
    await sync_food_log(food_log_in_db.dict(by_alias=True))
    
    return food_log_in_db


async def get_food_log_by_id(food_log_id: str) -> Optional[FoodLogInDB]:
    """
    Get a food log by ID.
    
    Args:
        food_log_id: Food log ID
        
    Returns:
        Food log or None if not found
    """
    db = await get_database()
    
    food_log_data = await db.food_logs.find_one({"_id": ObjectId(food_log_id)})
    if food_log_data:
        return FoodLogInDB(**food_log_data)
    
    return None


async def update_food_log(food_log_id: str, food_log_update: FoodLogUpdate) -> Optional[FoodLogInDB]:
    """
    Update a food log.
    
    Args:
        food_log_id: Food log ID
        food_log_update: Food log update data
        
    Returns:
        Updated food log or None if not found
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in food_log_update.dict().items() if v is not None}
    
    # Calculate totals if meals are updated but totals are not
    if "meals" in update_data and "total_calories" not in update_data:
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for meal in update_data["meals"]:
            for food_item in meal.foods:
                if "calories" in food_item:
                    total_calories += food_item["calories"] * food_item.get("quantity", 1)
                if "protein" in food_item:
                    total_protein += food_item["protein"] * food_item.get("quantity", 1)
                if "carbs" in food_item:
                    total_carbs += food_item["carbs"] * food_item.get("quantity", 1)
                if "fat" in food_item:
                    total_fat += food_item["fat"] * food_item.get("quantity", 1)
        
        update_data["total_calories"] = total_calories
        update_data["total_protein"] = total_protein
        update_data["total_carbs"] = total_carbs
        update_data["total_fat"] = total_fat
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the food log
    result = await db.food_logs.update_one(
        {"_id": ObjectId(food_log_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated food log
        updated_food_log = await get_food_log_by_id(food_log_id)
        
        # Update in Elasticsearch
        if updated_food_log:
            await sync_food_log(updated_food_log.dict(by_alias=True), operation="update")
            
        return updated_food_log
    
    return None


async def delete_food_log(food_log_id: str) -> bool:
    """
    Delete a food log.
    
    Args:
        food_log_id: Food log ID
        
    Returns:
        True if food log was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.food_logs.delete_one({"_id": ObjectId(food_log_id)})
    
    # Delete from Elasticsearch
    if result.deleted_count:
        await sync_food_log({"_id": food_log_id}, operation="delete")
        
    return result.deleted_count > 0


async def get_user_food_logs(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "date",
    sort_direction: int = -1
) -> List[FoodLogInDB]:
    """
    Get a user's food logs with pagination and date range filter.
    
    Args:
        user_id: User ID
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        skip: Number of food logs to skip
        limit: Maximum number of food logs to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of food logs
    """
    db = await get_database()
    food_logs = []
    
    # Build query filters
    filters = {"user_id": ObjectId(user_id)}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            date_filter["$gte"] = start_datetime
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            date_filter["$lte"] = end_datetime
        filters["date"] = date_filter
    
    cursor = db.food_logs.find(filters).sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    async for food_log_data in cursor:
        food_logs.append(FoodLogInDB(**food_log_data))
    
    return food_logs


async def add_meal_to_food_log(food_log_id: str, meal: MealBase) -> Optional[FoodLogInDB]:
    """
    Add a meal to an existing food log.
    
    Args:
        food_log_id: Food log ID
        meal: Meal to add
        
    Returns:
        Updated food log or None if not found
    """
    db = await get_database()
    
    # Get the current food log to calculate new totals
    current_food_log = await get_food_log_by_id(food_log_id)
    if not current_food_log:
        return None
    
    # Calculate additional nutrition from the meal
    additional_calories = 0
    additional_protein = 0
    additional_carbs = 0
    additional_fat = 0
    
    for food_item in meal.foods:
        if "calories" in food_item:
            additional_calories += food_item["calories"] * food_item.get("quantity", 1)
        if "protein" in food_item:
            additional_protein += food_item["protein"] * food_item.get("quantity", 1)
        if "carbs" in food_item:
            additional_carbs += food_item["carbs"] * food_item.get("quantity", 1)
        if "fat" in food_item:
            additional_fat += food_item["fat"] * food_item.get("quantity", 1)
    
    # Update the food log
    result = await db.food_logs.update_one(
        {"_id": ObjectId(food_log_id)},
        {
            "$push": {"meals": meal.dict()},
            "$inc": {
                "total_calories": additional_calories,
                "total_protein": additional_protein,
                "total_carbs": additional_carbs,
                "total_fat": additional_fat
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count:
        # Get the updated food log
        updated_food_log = await get_food_log_by_id(food_log_id)
        
        # Update in Elasticsearch
        if updated_food_log:
            await sync_food_log(updated_food_log.dict(by_alias=True), operation="update")
            
        return updated_food_log
    
    return None


async def get_nutrition_summary(
    user_id: str,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Get a summary of a user's nutrition over a date range.
    
    Args:
        user_id: User ID
        start_date: Start date
        end_date: End date
        
    Returns:
        Nutrition summary
    """
    db = await get_database()
    
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Aggregate to get summary
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "date": {
                    "$gte": start_datetime,
                    "$lte": end_datetime
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_calories": {"$avg": "$total_calories"},
                "avg_protein": {"$avg": "$total_protein"},
                "avg_carbs": {"$avg": "$total_carbs"},
                "avg_fat": {"$avg": "$total_fat"},
                "max_calories": {"$max": "$total_calories"},
                "max_protein": {"$max": "$total_protein"},
                "max_carbs": {"$max": "$total_carbs"},
                "max_fat": {"$max": "$total_fat"},
                "min_calories": {"$min": "$total_calories"},
                "min_protein": {"$min": "$total_protein"},
                "min_carbs": {"$min": "$total_carbs"},
                "min_fat": {"$min": "$total_fat"},
                "total_logs": {"$sum": 1},
                "avg_water_intake": {"$avg": "$water_intake"}
            }
        }
    ]
    
    result = await db.food_logs.aggregate(pipeline).to_list(length=1)
    
    if result:
        summary = result[0]
        # Remove _id field
        if "_id" in summary:
            del summary["_id"]
        return summary
    
    # Return empty summary if no logs found
    return {
        "avg_calories": 0,
        "avg_protein": 0,
        "avg_carbs": 0,
        "avg_fat": 0,
        "max_calories": 0,
        "max_protein": 0,
        "max_carbs": 0,
        "max_fat": 0,
        "min_calories": 0,
        "min_protein": 0,
        "min_carbs": 0,
        "min_fat": 0,
        "total_logs": 0,
        "avg_water_intake": 0
    } 