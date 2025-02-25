from typing import Dict, List, Optional, Any, Tuple, Union
from elasticsearch import AsyncElasticsearch
from app.db.elasticsearch.elasticsearch import get_elasticsearch_client
from app.db.elasticsearch.indices import (
    WORKOUT_INDEX,
    USER_INDEX,
    FOOD_LOG_INDEX,
    MEASUREMENT_INDEX,
    GOAL_INDEX,
    SOCIAL_POST_INDEX
)


class SearchService:
    """Service for handling search operations across different entities."""

    @staticmethod
    async def search_workouts(
        query: str,
        user_id: Optional[str] = None,
        is_public: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search workouts based on the provided query and filters.
        
        Args:
            query: Search query
            user_id: Filter by user ID
            is_public: Filter by visibility
            date_from: Start date filter (YYYY-MM-DD)
            date_to: End date filter (YYYY-MM-DD)
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results with total count and workout documents
        """
        client = await get_elasticsearch_client()
        
        # Build filters
        filters = []
        if user_id:
            filters.append({"term": {"user_id": user_id}})
        if is_public is not None:
            filters.append({"term": {"is_public": is_public}})
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            filters.append({"range": {"date": date_range}})
            
        # Build search query
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "description^2", "exercises.name^2", "exercises.notes"]
                        }
                    },
                    "filter": filters
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {},
                    "exercises.name": {},
                    "exercises.notes": {}
                }
            }
        }
        
        response = await client.search(index=WORKOUT_INDEX, body=search_query)
        return response

    @staticmethod
    async def search_users(
        query: str,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search users based on the provided query.
        
        Args:
            query: Search query
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results with total count and user documents
        """
        client = await get_elasticsearch_client()
        
        # Build search query
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["username^3", "full_name^2", "bio"]
                }
            },
            "highlight": {
                "fields": {
                    "username": {},
                    "full_name": {},
                    "bio": {}
                }
            }
        }
        
        response = await client.search(index=USER_INDEX, body=search_query)
        return response

    @staticmethod
    async def search_food_logs(
        query: str,
        user_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search food logs based on the provided query and filters.
        
        Args:
            query: Search query
            user_id: Filter by user ID
            date_from: Start date filter (YYYY-MM-DD)
            date_to: End date filter (YYYY-MM-DD)
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results with total count and food log documents
        """
        client = await get_elasticsearch_client()
        
        # Build filters
        filters = []
        if user_id:
            filters.append({"term": {"user_id": user_id}})
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            filters.append({"range": {"date": date_range}})
            
        # Build search query with nested query for meals and foods
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {
                                        "multi_match": {
                                            "query": query,
                                            "fields": ["notes"]
                                        }
                                    },
                                    {
                                        "nested": {
                                            "path": "meals",
                                            "query": {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "nested": {
                                                                "path": "meals.foods",
                                                                "query": {
                                                                    "match": {
                                                                        "meals.foods.name": query
                                                                    }
                                                                },
                                                                "inner_hits": {}
                                                            }
                                                        }
                                                    ]
                                                }
                                            },
                                            "inner_hits": {}
                                        }
                                    }
                                ]
                            }
                        }
                    ],
                    "filter": filters
                }
            },
            "highlight": {
                "fields": {
                    "notes": {},
                    "meals.foods.name": {}
                }
            }
        }
        
        response = await client.search(index=FOOD_LOG_INDEX, body=search_query)
        return response

    @staticmethod
    async def search_goals(
        query: str,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        goal_type: Optional[str] = None,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search goals based on the provided query and filters.
        
        Args:
            query: Search query
            user_id: Filter by user ID
            status: Filter by goal status
            goal_type: Filter by goal type
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results with total count and goal documents
        """
        client = await get_elasticsearch_client()
        
        # Build filters
        filters = []
        if user_id:
            filters.append({"term": {"user_id": user_id}})
        if status:
            filters.append({"term": {"status": status}})
        if goal_type:
            filters.append({"term": {"goal_type": goal_type}})
            
        # Build search query
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "description^2"]
                        }
                    },
                    "filter": filters
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {}
                }
            }
        }
        
        response = await client.search(index=GOAL_INDEX, body=search_query)
        return response

    @staticmethod
    async def search_social_posts(
        query: str,
        user_id: Optional[str] = None,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search social posts based on the provided query and filters.
        
        Args:
            query: Search query
            user_id: Filter by user ID
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results with total count and social post documents
        """
        client = await get_elasticsearch_client()
        
        # Build filters
        filters = []
        if user_id:
            filters.append({"term": {"user_id": user_id}})
            
        # Build search query
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "content": query
                        }
                    },
                    "filter": filters
                }
            },
            "highlight": {
                "fields": {
                    "content": {}
                }
            }
        }
        
        response = await client.search(index=SOCIAL_POST_INDEX, body=search_query)
        return response

    @staticmethod
    async def search_all(
        query: str,
        user_id: Optional[str] = None,
        from_: int = 0,
        size: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all entity types.
        
        Args:
            query: Search query
            user_id: Filter by user ID
            from_: Starting document offset
            size: Number of documents to return
            
        Returns:
            Search results grouped by entity type
        """
        # Execute searches in parallel
        workouts_future = SearchService.search_workouts(
            query=query, 
            user_id=user_id, 
            is_public=True,
            from_=from_, 
            size=size
        )
        
        users_future = SearchService.search_users(
            query=query,
            from_=from_,
            size=size
        )
        
        food_logs_future = SearchService.search_food_logs(
            query=query,
            user_id=user_id if user_id else None,
            from_=from_,
            size=size
        )
        
        goals_future = SearchService.search_goals(
            query=query,
            user_id=user_id if user_id else None,
            from_=from_,
            size=size
        )
        
        social_posts_future = SearchService.search_social_posts(
            query=query,
            from_=from_,
            size=size
        )
        
        # Get the results
        workouts_result = await workouts_future
        users_result = await users_future
        food_logs_result = await food_logs_future
        goals_result = await goals_future
        social_posts_result = await social_posts_future
        
        # Process and combine the results
        results = {
            "workouts": {
                "total": workouts_result["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in workouts_result["hits"]["hits"]]
            },
            "users": {
                "total": users_result["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in users_result["hits"]["hits"]]
            },
            "food_logs": {
                "total": food_logs_result["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in food_logs_result["hits"]["hits"]]
            },
            "goals": {
                "total": goals_result["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in goals_result["hits"]["hits"]]
            },
            "social_posts": {
                "total": social_posts_result["hits"]["total"]["value"],
                "results": [hit["_source"] for hit in social_posts_result["hits"]["hits"]]
            }
        }
        
        return results


# Helper functions to format search results
def format_workout_search_results(es_response: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Format workout search results from Elasticsearch response."""
    total = es_response["hits"]["total"]["value"]
    results = []
    
    for hit in es_response["hits"]["hits"]:
        workout = hit["_source"]
        
        # Add highlights if available
        if "highlight" in hit:
            workout["highlights"] = hit["highlight"]
            
        results.append(workout)
        
    return total, results
    
    
def format_user_search_results(es_response: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Format user search results from Elasticsearch response."""
    total = es_response["hits"]["total"]["value"]
    results = []
    
    for hit in es_response["hits"]["hits"]:
        user = hit["_source"]
        
        # Add highlights if available
        if "highlight" in hit:
            user["highlights"] = hit["highlight"]
            
        results.append(user)
        
    return total, results


def format_food_log_search_results(es_response: Dict[str, Any]) -> Tuple[int, List[Dict[str, Any]]]:
    """Format food log search results from Elasticsearch response."""
    total = es_response["hits"]["total"]["value"]
    results = []
    
    for hit in es_response["hits"]["hits"]:
        food_log = hit["_source"]
        
        # Add highlights if available
        if "highlight" in hit:
            food_log["highlights"] = hit["highlight"]
            
        # Add inner hits for nested fields if available
        if "inner_hits" in hit:
            food_log["matched_items"] = []
            
            if "meals" in hit["inner_hits"]:
                for meal_hit in hit["inner_hits"]["meals"]["hits"]["hits"]:
                    meal_idx = meal_hit["_nested"]["offset"]
                    
                    if "meals.foods" in meal_hit["inner_hits"]:
                        for food_hit in meal_hit["inner_hits"]["meals.foods"]["hits"]["hits"]:
                            food_idx = food_hit["_nested"]["offset"]
                            food_name = food_hit["_source"]["name"]
                            
                            food_log["matched_items"].append({
                                "meal_index": meal_idx,
                                "food_index": food_idx,
                                "food_name": food_name
                            })
            
        results.append(food_log)
        
    return total, results 