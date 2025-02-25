from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from datetime import datetime

from app.core.security import get_current_active_user
from app.models.user import User
from app.db.mongodb.search import MongoDBSearchService

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
    Search workouts.
    
    Args:
        q: Search query
        date_from: Start date filter (ISO format)
        date_to: End date filter (ISO format)
        page: Page number
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results
    """
    skip = page * page_size
    return await MongoDBSearchService.search_workouts(
        query=q,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=page_size
    )


@router.get("/users")
async def search_users(
    q: str,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search users.
    
    Args:
        q: Search query
        page: Page number
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results
    """
    skip = page * page_size
    return await MongoDBSearchService.search_users(
        query=q,
        skip=skip,
        limit=page_size
    )


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
    Search food logs.
    
    Args:
        q: Search query
        date_from: Start date filter (ISO format)
        date_to: End date filter (ISO format)
        page: Page number
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Search results
    """
    skip = page * page_size
    return await MongoDBSearchService.search_food_logs(
        query=q,
        user_id=str(current_user.id),
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=page_size
    )


@router.get("/")
async def search_all(
    q: str,
    page: int = 0,
    page_size: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search across all collections.
    
    Args:
        q: Search query
        page: Page number
        page_size: Number of results per page
        current_user: Current authenticated user
        
    Returns:
        Combined search results
    """
    skip = page * page_size
    return await MongoDBSearchService.search_all(
        query=q,
        user_id=str(current_user.id),
        skip=skip,
        limit=page_size
    ) 