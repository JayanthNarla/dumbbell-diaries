from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from bson import ObjectId
from datetime import datetime

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workout import WorkoutWithUserInfo


router = APIRouter()


# Post model (simple version for the social feed)
class Post:
    id: str
    user_id: str
    user_name: str
    user_profile_picture: Optional[str]
    content: str
    media_urls: Optional[List[str]]
    created_at: datetime
    likes_count: int
    comments_count: int
    workout_id: Optional[str]  # Reference to a workout if any


# Comment model
class Comment:
    id: str
    post_id: str
    user_id: str
    user_name: str
    user_profile_picture: Optional[str]
    content: str
    created_at: datetime
    likes_count: int


# Mock database functions
async def get_social_feed_db(
    user_id: str,
    feed_type: str = "following",  # "following", "discover"
    skip: int = 0,
    limit: int = 20
) -> List[Dict]:
    """Get user's social feed."""
    # This would be replaced with actual DB call
    return []


async def create_post_db(
    user_id: str,
    content: str,
    media_urls: Optional[List[str]] = None,
    workout_id: Optional[str] = None
) -> Dict:
    """Create a social post."""
    # This would be replaced with actual DB call
    post_id = str(ObjectId())
    return {
        "id": post_id,
        "user_id": user_id,
        "content": content,
        "media_urls": media_urls or [],
        "created_at": datetime.utcnow(),
        "likes_count": 0,
        "comments_count": 0,
        "workout_id": workout_id
    }


async def get_post_by_id_db(post_id: str) -> Optional[Dict]:
    """Get a post by ID."""
    # This would be replaced with actual DB call
    return None


async def delete_post_db(post_id: str) -> bool:
    """Delete a post."""
    # This would be replaced with actual DB call
    return True


async def like_post_db(post_id: str, user_id: str) -> Dict:
    """Like a post."""
    # This would be replaced with actual DB call
    return {"likes_count": 1}


async def unlike_post_db(post_id: str, user_id: str) -> Dict:
    """Unlike a post."""
    # This would be replaced with actual DB call
    return {"likes_count": 0}


async def add_comment_db(post_id: str, user_id: str, content: str) -> Dict:
    """Add a comment to a post."""
    # This would be replaced with actual DB call
    comment_id = str(ObjectId())
    return {
        "id": comment_id,
        "post_id": post_id,
        "user_id": user_id,
        "content": content,
        "created_at": datetime.utcnow(),
        "likes_count": 0
    }


async def get_post_comments_db(post_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
    """Get comments for a post."""
    # This would be replaced with actual DB call
    return []


@router.get("/feed", response_model=List[Dict])
async def get_social_feed(
    feed_type: str = "following",
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get user's social feed.
    
    Args:
        feed_type: Type of feed ("following" or "discover")
        skip: Number of posts to skip
        limit: Maximum number of posts to return
        current_user: Current authenticated user
        
    Returns:
        List of social posts
    """
    return await get_social_feed_db(str(current_user.id), feed_type, skip, limit)


@router.post("/posts", response_model=Dict)
async def create_post(
    content: str = Body(..., embed=True),
    media_urls: Optional[List[str]] = Body(None, embed=True),
    workout_id: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new social post.
    
    Args:
        content: Post content
        media_urls: Optional list of media URLs
        workout_id: Optional reference to a workout
        current_user: Current authenticated user
        
    Returns:
        Created post
    """
    return await create_post_db(str(current_user.id), content, media_urls, workout_id)


@router.get("/posts/{post_id}", response_model=Dict)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a post by ID.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        Post
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return post


@router.delete("/posts/{post_id}", response_model=bool)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a post.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        True if post was deleted
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Check if the post belongs to the current user
    if post["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_post_db(post_id)
    return result


@router.post("/posts/{post_id}/like", response_model=Dict)
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Like a post.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        Post like count
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    result = await like_post_db(post_id, str(current_user.id))
    return result


@router.post("/posts/{post_id}/unlike", response_model=Dict)
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unlike a post.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        Post like count
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    result = await unlike_post_db(post_id, str(current_user.id))
    return result


@router.post("/posts/{post_id}/comments", response_model=Dict)
async def add_comment(
    post_id: str,
    content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a comment to a post.
    
    Args:
        post_id: Post ID
        content: Comment content
        current_user: Current authenticated user
        
    Returns:
        Created comment
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    result = await add_comment_db(post_id, str(current_user.id), content)
    return result


@router.get("/posts/{post_id}/comments", response_model=List[Dict])
async def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get comments for a post.
    
    Args:
        post_id: Post ID
        skip: Number of comments to skip
        limit: Maximum number of comments to return
        current_user: Current authenticated user
        
    Returns:
        List of comments
    """
    post = await get_post_by_id_db(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return await get_post_comments_db(post_id, skip, limit)


@router.get("/workouts/trending", response_model=List[WorkoutWithUserInfo])
async def get_trending_workouts(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get trending workouts based on social interaction metrics.
    
    Args:
        skip: Number of workouts to skip
        limit: Maximum number of workouts to return
        current_user: Current authenticated user
        
    Returns:
        List of trending workouts with user info
    """
    # This would be replaced with actual DB call
    return []
