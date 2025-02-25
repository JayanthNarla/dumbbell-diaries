from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.db.mongodb.users import (
    get_user_by_id,
    update_user,
    delete_user,
    get_all_users,
    add_follower,
    remove_follower
)
from app.models.user import User, UserUpdate


router = APIRouter()


@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user info
    """
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update current user.
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        
    Returns:
        Updated user info
    """
    user = await update_user(str(current_user.id), user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        
    Returns:
        User info
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", response_model=bool)
async def delete_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        
    Returns:
        True if user was deleted
    """
    # Check if current user is admin or the user being deleted
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_user(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return result


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all users (admin only).
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Current authenticated user
        
    Returns:
        List of users
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    users = await get_all_users(skip=skip, limit=limit)
    return users


@router.post("/{user_id}/follow", response_model=bool)
async def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Follow a user.
    
    Args:
        user_id: User ID to follow
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    # Check if trying to follow self
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself",
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    result = await add_follower(user_id, str(current_user.id))
    return result


@router.post("/{user_id}/unfollow", response_model=bool)
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unfollow a user.
    
    Args:
        user_id: User ID to unfollow
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    # Check if trying to unfollow self
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unfollow yourself",
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    result = await remove_follower(user_id, str(current_user.id))
    return result
