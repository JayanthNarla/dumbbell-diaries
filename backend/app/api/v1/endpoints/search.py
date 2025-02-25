from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_active_user
from app.models.user import User
from app.db.elasticsearch.search import (
    SearchService,
    format_workout_search_results,
    format_user_search_results,
    format_food_log_search_results
)


router = APIRouter()


@router.get("/workouts")
async def search_workouts(
    q: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search workouts based on the query string.
    
    Args:
        q: Search query
        date_from: Optional start date (YYYY-MM-DD) for filtering
        date_to: Optional end date (YYYY-MM-DD) for filtering
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results with total count and workout documents
    """
    from_ = page * page_size
    
    # Search for user's workouts and public workouts
    es_response = await SearchService.search_workouts(
        query=q,
        user_id=str(current_user.id),
        date_from=date_from,
        date_to=date_to,
        from_=from_,
        size=page_size
    )
    
    total, results = format_workout_search_results(es_response)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }


@router.get("/users")
async def search_users(
    q: str,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search users based on the query string.
    
    Args:
        q: Search query
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results with total count and user documents
    """
    from_ = page * page_size
    
    es_response = await SearchService.search_users(
        query=q,
        from_=from_,
        size=page_size
    )
    
    total, results = format_user_search_results(es_response)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }


@router.get("/food-logs")
async def search_food_logs(
    q: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search food logs based on the query string.
    
    Args:
        q: Search query
        date_from: Optional start date (YYYY-MM-DD) for filtering
        date_to: Optional end date (YYYY-MM-DD) for filtering
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results with total count and food log documents
    """
    from_ = page * page_size
    
    # Only search user's own food logs
    es_response = await SearchService.search_food_logs(
        query=q,
        user_id=str(current_user.id),
        date_from=date_from,
        date_to=date_to,
        from_=from_,
        size=page_size
    )
    
    total, results = format_food_log_search_results(es_response)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }


@router.get("/goals")
async def search_goals(
    q: str,
    status: Optional[str] = None,
    goal_type: Optional[str] = None,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search goals based on the query string.
    
    Args:
        q: Search query
        status: Optional goal status filter
        goal_type: Optional goal type filter
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results with total count and goal documents
    """
    from_ = page * page_size
    
    # Only search user's own goals
    es_response = await SearchService.search_goals(
        query=q,
        user_id=str(current_user.id),
        status=status,
        goal_type=goal_type,
        from_=from_,
        size=page_size
    )
    
    # Format the results
    total = es_response["hits"]["total"]["value"]
    results = []
    
    for hit in es_response["hits"]["hits"]:
        goal = hit["_source"]
        
        # Add highlights if available
        if "highlight" in hit:
            goal["highlights"] = hit["highlight"]
            
        results.append(goal)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }


@router.get("/social-posts")
async def search_social_posts(
    q: str,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search social posts based on the query string.
    
    Args:
        q: Search query
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results with total count and social post documents
    """
    from_ = page * page_size
    
    # Search for all public posts or user's own posts
    es_response = await SearchService.search_social_posts(
        query=q,
        from_=from_,
        size=page_size
    )
    
    # Format the results
    total = es_response["hits"]["total"]["value"]
    results = []
    
    for hit in es_response["hits"]["hits"]:
        post = hit["_source"]
        
        # Add highlights if available
        if "highlight" in hit:
            post["highlights"] = hit["highlight"]
            
        results.append(post)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": results
    }


@router.get("/")
async def search_all(
    q: str,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search across all entity types based on the query string.
    
    Args:
        q: Search query
        page: Page number (0-indexed)
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results grouped by entity type
    """
    from_ = page * page_size
    
    # Search across all entities
    results = await SearchService.search_all(
        query=q,
        user_id=str(current_user.id),
        from_=from_,
        size=page_size
    )
    
    return {
        "page": page,
        "page_size": page_size,
        "results": results
    } 