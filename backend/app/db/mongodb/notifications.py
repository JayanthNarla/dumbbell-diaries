from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.notification import (
    NotificationCreate, 
    NotificationInDB,
    NotificationType,
    NotificationSettingsUpdate,
    NotificationSettingsInDB
)
from app.db.mongodb.mongodb import get_database


async def create_notification(notification: NotificationCreate, user_id: str) -> NotificationInDB:
    """
    Create a new notification.
    
    Args:
        notification: Notification data
        user_id: User ID
        
    Returns:
        Created notification
    """
    db = await get_database()
    
    notification_in_db = NotificationInDB(
        **notification.dict(),
        user_id=ObjectId(user_id),
        created_at=datetime.utcnow(),
        is_read=False
    )
    
    result = await db.notifications.insert_one(notification_in_db.dict(by_alias=True))
    notification_in_db.id = result.inserted_id
    
    return notification_in_db


async def get_notification_by_id(notification_id: str) -> Optional[NotificationInDB]:
    """
    Get a notification by ID.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        Notification or None if not found
    """
    db = await get_database()
    
    notification_data = await db.notifications.find_one({"_id": ObjectId(notification_id)})
    if notification_data:
        return NotificationInDB(**notification_data)
    
    return None


async def mark_notification_read(notification_id: str) -> Optional[NotificationInDB]:
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        Updated notification or None if not found
    """
    db = await get_database()
    
    result = await db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count:
        return await get_notification_by_id(notification_id)
    
    return None


async def delete_notification(notification_id: str) -> bool:
    """
    Delete a notification.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        True if notification was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.notifications.delete_one({"_id": ObjectId(notification_id)})
    
    return result.deleted_count > 0


async def get_user_notifications(
    user_id: str,
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_direction: int = -1
) -> List[NotificationInDB]:
    """
    Get a user's notifications with pagination and filters.
    
    Args:
        user_id: User ID
        is_read: Optional filter for read status
        notification_type: Optional filter for notification type
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of notifications
    """
    db = await get_database()
    notifications = []
    
    # Build query filters
    filters = {"user_id": ObjectId(user_id)}
    
    if is_read is not None:
        filters["is_read"] = is_read
    
    if notification_type:
        filters["type"] = notification_type
    
    cursor = db.notifications.find(filters).sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    async for notification_data in cursor:
        notifications.append(NotificationInDB(**notification_data))
    
    return notifications


async def mark_all_notifications_read(user_id: str) -> int:
    """
    Mark all notifications as read for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Number of notifications marked as read
    """
    db = await get_database()
    
    result = await db.notifications.update_many(
        {"user_id": ObjectId(user_id), "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return result.modified_count


async def create_user_notification_settings(user_id: str) -> NotificationSettingsInDB:
    """
    Create default notification settings for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Created notification settings
    """
    db = await get_database()
    
    # Default settings (all enabled)
    settings = NotificationSettingsInDB(
        user_id=ObjectId(user_id),
        workout_reminders=True,
        goal_updates=True,
        social_interactions=True,
        achievement_notifications=True,
        system_notifications=True,
        email_notifications=True,
        push_notifications=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Check if settings already exist
    existing_settings = await db.notification_settings.find_one({"user_id": ObjectId(user_id)})
    
    if not existing_settings:
        await db.notification_settings.insert_one(settings.dict(by_alias=True))
    
    return settings


async def get_user_notification_settings(user_id: str) -> NotificationSettingsInDB:
    """
    Get a user's notification settings.
    
    Args:
        user_id: User ID
        
    Returns:
        Notification settings
    """
    db = await get_database()
    
    settings_data = await db.notification_settings.find_one({"user_id": ObjectId(user_id)})
    
    if not settings_data:
        # Create default settings if not found
        return await create_user_notification_settings(user_id)
    
    return NotificationSettingsInDB(**settings_data)


async def update_user_notification_settings(
    user_id: str,
    settings_update: NotificationSettingsUpdate
) -> NotificationSettingsInDB:
    """
    Update a user's notification settings.
    
    Args:
        user_id: User ID
        settings_update: Settings update data
        
    Returns:
        Updated notification settings
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in settings_update.dict().items() if v is not None}
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Create settings if they don't exist
    await create_user_notification_settings(user_id)
    
    # Update the settings
    await db.notification_settings.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    # Get updated settings
    return await get_user_notification_settings(user_id)


async def register_device_token(user_id: str, device_token: str, device_type: str) -> bool:
    """
    Register a device token for push notifications.
    
    Args:
        user_id: User ID
        device_token: Device token
        device_type: Device type (e.g., "ios", "android", "web")
        
    Returns:
        True if successfully registered
    """
    db = await get_database()
    
    device_data = {
        "user_id": ObjectId(user_id),
        "device_token": device_token,
        "device_type": device_type,
        "created_at": datetime.utcnow(),
        "last_used": datetime.utcnow()
    }
    
    # Upsert to avoid duplicates
    await db.device_tokens.update_one(
        {"user_id": ObjectId(user_id), "device_token": device_token},
        {"$set": device_data},
        upsert=True
    )
    
    return True


async def unregister_device_token(user_id: str, device_token: str) -> bool:
    """
    Unregister a device token.
    
    Args:
        user_id: User ID
        device_token: Device token
        
    Returns:
        True if successfully unregistered, False if not found
    """
    db = await get_database()
    
    result = await db.device_tokens.delete_one({
        "user_id": ObjectId(user_id),
        "device_token": device_token
    })
    
    return result.deleted_count > 0


async def get_user_device_tokens(user_id: str) -> List[Dict[str, Any]]:
    """
    Get a user's device tokens.
    
    Args:
        user_id: User ID
        
    Returns:
        List of device tokens
    """
    db = await get_database()
    
    cursor = db.device_tokens.find({"user_id": ObjectId(user_id)})
    
    device_tokens = []
    async for token_data in cursor:
        # Convert ObjectId to string
        token_data["_id"] = str(token_data["_id"])
        token_data["user_id"] = str(token_data["user_id"])
        device_tokens.append(token_data)
    
    return device_tokens


async def send_notification_to_user(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[NotificationInDB]:
    """
    Send a notification to a user.
    
    Args:
        user_id: User ID
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        metadata: Optional metadata
        
    Returns:
        Created notification or None if user has disabled this type
    """
    db = await get_database()
    
    # Check user's settings
    settings = await get_user_notification_settings(user_id)
    
    # Check if this type of notification is enabled
    if notification_type == NotificationType.WORKOUT_REMINDER and not settings.workout_reminders:
        return None
    elif notification_type == NotificationType.GOAL_UPDATE and not settings.goal_updates:
        return None
    elif notification_type == NotificationType.SOCIAL and not settings.social_interactions:
        return None
    elif notification_type == NotificationType.ACHIEVEMENT and not settings.achievement_notifications:
        return None
    elif notification_type == NotificationType.SYSTEM and not settings.system_notifications:
        return None
    
    # Create the notification
    notification = NotificationCreate(
        title=title,
        message=message,
        type=notification_type,
        metadata=metadata or {}
    )
    
    return await create_notification(notification, user_id)


async def get_unread_notification_count(user_id: str) -> int:
    """
    Get count of unread notifications for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Count of unread notifications
    """
    db = await get_database()
    
    count = await db.notifications.count_documents({
        "user_id": ObjectId(user_id),
        "is_read": False
    })
    
    return count 