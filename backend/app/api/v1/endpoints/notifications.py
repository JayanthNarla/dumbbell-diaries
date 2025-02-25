from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from bson import ObjectId
from datetime import datetime

from app.core.security import get_current_active_user
from app.models.user import User


router = APIRouter()


# Simple notification model
class Notification:
    id: str
    user_id: str
    type: str  # e.g., "follow", "like", "comment", "goal_achieved", "reminder"
    title: str
    message: str
    is_read: bool
    created_at: datetime
    metadata: Optional[Dict]  # Additional data specific to notification type


# Mock database functions
async def get_user_notifications_db(
    user_id: str,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Dict]:
    """Get user's notifications."""
    # This would be replaced with actual DB call
    return []


async def mark_notification_read_db(notification_id: str, user_id: str) -> bool:
    """Mark a notification as read."""
    # This would be replaced with actual DB call
    return True


async def mark_all_notifications_read_db(user_id: str) -> bool:
    """Mark all notifications as read for a user."""
    # This would be replaced with actual DB call
    return True


async def delete_notification_db(notification_id: str, user_id: str) -> bool:
    """Delete a notification."""
    # This would be replaced with actual DB call
    return True


async def register_device_token_db(user_id: str, device_token: str, device_type: str) -> bool:
    """Register a device token for push notifications."""
    # This would be replaced with actual DB call
    return True


async def unregister_device_token_db(user_id: str, device_token: str) -> bool:
    """Unregister a device token."""
    # This would be replaced with actual DB call
    return True


@router.get("/", response_model=List[Dict])
async def get_notifications(
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's notifications.
    
    Args:
        is_read: Filter by read status
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        current_user: Current authenticated user
        
    Returns:
        List of notifications
    """
    return await get_user_notifications_db(str(current_user.id), is_read, skip, limit)


@router.put("/{notification_id}/read", response_model=bool)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    result = await mark_notification_read_db(notification_id, str(current_user.id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return result


@router.put("/read-all", response_model=bool)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Mark all notifications as read.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    return await mark_all_notifications_read_db(str(current_user.id))


@router.delete("/{notification_id}", response_model=bool)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a notification.
    
    Args:
        notification_id: Notification ID
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    result = await delete_notification_db(notification_id, str(current_user.id))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return result


@router.post("/devices", response_model=bool)
async def register_device(
    device_token: str = Body(..., embed=True),
    device_type: str = Body(..., embed=True),  # "ios", "android", "web"
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Register a device token for push notifications.
    
    Args:
        device_token: Device token for push notifications
        device_type: Type of device
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    return await register_device_token_db(str(current_user.id), device_token, device_type)


@router.delete("/devices/{device_token}", response_model=bool)
async def unregister_device(
    device_token: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unregister a device token.
    
    Args:
        device_token: Device token to unregister
        current_user: Current authenticated user
        
    Returns:
        True if successful
    """
    return await unregister_device_token_db(str(current_user.id), device_token)


@router.get("/settings", response_model=Dict)
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's notification settings.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Notification settings
    """
    # This would be replaced with actual DB call
    return {
        "push_enabled": True,
        "email_enabled": True,
        "categories": {
            "social": True,
            "workout_reminders": True,
            "goal_updates": True,
            "achievements": True
        }
    }


@router.put("/settings", response_model=Dict)
async def update_notification_settings(
    settings: Dict = Body(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update current user's notification settings.
    
    Args:
        settings: Notification settings to update
        current_user: Current authenticated user
        
    Returns:
        Updated notification settings
    """
    # This would be replaced with actual DB call
    return settings
