from typing import Dict, List, Any, Optional
from datetime import datetime
from bson import ObjectId

from app.db.mongodb.mongodb import get_database


class MongoDBSearchService:
    """Service for handling search operations using MongoDB Atlas Search."""

    @staticmethod
    async def search_workouts(
        query: str,
        user_id: Optional[str] = None,
        is_public: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search workouts using Atlas Search.
        """
        db = await get_database()
        
        # Build search pipeline
        pipeline = [
            {
                "$search": {
                    "index": "workouts",  # You'll need to create this index in Atlas
                    "text": {
                        "query": query,
                        "path": ["title", "description", "exercises.name", "exercises.notes"],
                        "fuzzy": {}
                    }
                }
            }
        ]

        # Add filters
        match_conditions = {}
        if user_id:
            match_conditions["user_id"] = ObjectId(user_id)
        if is_public is not None:
            match_conditions["is_public"] = is_public
        if date_from or date_to:
            date_condition = {}
            if date_from:
                date_condition["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_condition["$lte"] = datetime.fromisoformat(date_to)
            if date_condition:
                match_conditions["date"] = date_condition

        if match_conditions:
            pipeline.append({"$match": match_conditions})

        # Add pagination
        pipeline.extend([
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
                    "id": {"$toString": "$_id"},
                    "title": 1,
                    "description": 1,
                    "exercises": 1,
                    "date": 1,
                    "is_public": 1,
                    "likes_count": {"$size": "$likes"},
                    "comments_count": {"$size": "$comments"},
                    "user_name": "$user.username",
                    "user_profile_picture": "$user.profile_picture"
                }
            }
        ])

        # Execute search
        results = await db.workouts.aggregate(pipeline).to_list(length=None)
        total_count = len(results)  # In production, you'd want to optimize this

        return {
            "total": total_count,
            "results": results
        }

    @staticmethod
    async def search_users(
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search users using Atlas Search.
        """
        db = await get_database()
        
        pipeline = [
            {
                "$search": {
                    "index": "users",  # You'll need to create this index in Atlas
                    "text": {
                        "query": query,
                        "path": ["username", "full_name", "bio"],
                        "fuzzy": {}
                    }
                }
            },
            {"$skip": skip},
            {"$limit": limit},
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "username": 1,
                    "full_name": 1,
                    "profile_picture": 1,
                    "bio": 1,
                    "following_count": {"$size": "$following"},
                    "followers_count": {"$size": "$followers"},
                    "_id": 0
                }
            }
        ]

        results = await db.users.aggregate(pipeline).to_list(length=None)
        total_count = len(results)

        return {
            "total": total_count,
            "results": results
        }

    @staticmethod
    async def search_food_logs(
        query: str,
        user_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search food logs using Atlas Search.
        """
        db = await get_database()
        
        pipeline = [
            {
                "$search": {
                    "index": "food_logs",  # You'll need to create this index in Atlas
                    "text": {
                        "query": query,
                        "path": ["meals.meal_type", "meals.foods.name", "notes"],
                        "fuzzy": {}
                    }
                }
            }
        ]

        # Add filters
        match_conditions = {}
        if user_id:
            match_conditions["user_id"] = ObjectId(user_id)
        if date_from or date_to:
            date_condition = {}
            if date_from:
                date_condition["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_condition["$lte"] = datetime.fromisoformat(date_to)
            if date_condition:
                match_conditions["date"] = date_condition

        if match_conditions:
            pipeline.append({"$match": match_conditions})

        # Add pagination and projection
        pipeline.extend([
            {"$skip": skip},
            {"$limit": limit},
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "date": 1,
                    "meals": 1,
                    "total_calories": 1,
                    "total_protein": 1,
                    "total_carbs": 1,
                    "total_fat": 1,
                    "notes": 1,
                    "_id": 0
                }
            }
        ])

        results = await db.food_logs.aggregate(pipeline).to_list(length=None)
        total_count = len(results)

        return {
            "total": total_count,
            "results": results
        }

    @staticmethod
    async def search_all(
        query: str,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform a combined search across all searchable collections.
        """
        workouts = await MongoDBSearchService.search_workouts(query, user_id=user_id, skip=skip, limit=limit)
        users = await MongoDBSearchService.search_users(query, skip=skip, limit=limit)
        food_logs = await MongoDBSearchService.search_food_logs(query, user_id=user_id, skip=skip, limit=limit)

        return {
            "workouts": workouts["results"],
            "users": users["results"],
            "food_logs": food_logs["results"]
        } 