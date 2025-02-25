from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.models.user import UserInDB, UserCreate, UserUpdate, User
from app.core.security import get_password_hash
from app.db.mongodb.mongodb import get_database


async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """
    Get a user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User object or None if not found
    """
    db = await get_database()
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return UserInDB(**user_data)
    return None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get a user by email.
    
    Args:
        email: User email
        
    Returns:
        User object or None if not found
    """
    db = await get_database()
    user_data = await db.users.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """
    Get a user by username.
    
    Args:
        username: Username
        
    Returns:
        User object or None if not found
    """
    db = await get_database()
    user_data = await db.users.find_one({"username": username})
    print(user_data)
    if user_data:
        return UserInDB(**user_data)
    return None


async def create_user(user: UserCreate) -> UserInDB:
    """
    Create a new user with MongoDB-generated ID.
    
    Args:
        user: User data
        
    Returns:
        Created user object
    """
    db = await get_database()
    
    # Prepare user data WITHOUT explicitly setting _id
    user_data = {
        **user.dict(exclude={"password"}),
        "hashed_password": get_password_hash(user.password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Let MongoDB generate the ObjectId automatically
    result = await db.users.insert_one(user_data)
    
    # Create UserInDB with the generated ID
    # user_in_db = UserInDB(
    #     _id=str(result.inserted_id),  # Convert ObjectId to string
    #     **user_data
    # )

    return UserInDB(
         # Use alias mapping
        **user_data
    )
    
    

async def update_user(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
    """
    Update a user.
    
    Args:
        user_id: User ID
        user_update: User update data
        
    Returns:
        Updated user object or None if not found
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    # Handle password hashing if provided
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the user
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return await get_user_by_id(user_id)


async def delete_user(user_id: str) -> bool:
    """
    Delete a user.
    
    Args:
        user_id: User ID
        
    Returns:
        True if user was deleted, False otherwise
    """
    db = await get_database()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


async def get_all_users(skip: int = 0, limit: int = 100) -> List[UserInDB]:
    """
    Get all users with pagination.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        
    Returns:
        List of users
    """
    db = await get_database()
    users = []
    
    cursor = db.users.find().skip(skip).limit(limit)
    async for user_data in cursor:
        users.append(UserInDB(**user_data))
    
    return users


async def add_follower(user_id: str, follower_id: str) -> bool:
    """
    Add a follower to a user.
    
    Args:
        user_id: User ID
        follower_id: Follower's user ID
        
    Returns:
        True if successful, False otherwise
    """
    db = await get_database()
    
    # Add follower to user's followers list
    user_result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"followers": ObjectId(follower_id)}}
    )
    
    # Add user to follower's following list
    follower_result = await db.users.update_one(
        {"_id": ObjectId(follower_id)},
        {"$addToSet": {"following": ObjectId(user_id)}}
    )
    
    return user_result.modified_count > 0 and follower_result.modified_count > 0


async def remove_follower(user_id: str, follower_id: str) -> bool:
    """
    Remove a follower from a user.
    
    Args:
        user_id: User ID
        follower_id: Follower's user ID
        
    Returns:
        True if successful, False otherwise
    """
    db = await get_database()
    
    # Remove follower from user's followers list
    user_result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"followers": ObjectId(follower_id)}}
    )
    
    # Remove user from follower's following list
    follower_result = await db.users.update_one(
        {"_id": ObjectId(follower_id)},
        {"$pull": {"following": ObjectId(user_id)}}
    )
    
    return user_result.modified_count > 0 and follower_result.modified_count > 0 