from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from bson import ObjectId
from datetime import datetime
from app.models.social import PostCreate
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.workout import WorkoutWithUserInfo
from app.db.mongodb.social import (
    create_post,
    get_post_by_id,
    update_post,
    delete_post,
    like_post as like_post_db,
    unlike_post as unlike_post_db,
    add_comment,
    get_comments,
    get_social_feed,
    get_user_posts,
    follow_user as follow_user_db,
    unfollow_user as unfollow_user_db
)
from app.db.mongodb.search import search_content


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


@router.get("/feed", response_model=List[Dict])
async def get_social_feed_endpoint(
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
    return await get_social_feed(str(current_user.id), feed_type, skip, limit)

@router.post("/posts", response_model=Dict)
async def create_post_endpoint(
    post_data: Dict = Body(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Validate input using PostCreate model
    post_create = PostCreate(**post_data)
    
    return await create_post(
        post_create,
        user_id=(current_user.id)
    )
# @router.post("/posts", response_model=Dict)
# async def create_post_endpoint(
#     content: str = Body(..., embed=True),
#     media_urls: Optional[List[str]] = Body(None, embed=True),
#     workout_id: Optional[str] = Body(None, embed=True),
#     current_user: User = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Create a new social post.
    
#     Args:
#         content: Post content
#         media_urls: Optional list of media URLs
#         workout_id: Optional reference to a workout
#         current_user: Current authenticated user
        
#     Returns:
#         Created post
#     """
#     return await create_post(
#         {
#             "user_id": str(current_user.id),
#             "content": content,
#             "media_urls": media_urls,
#             "workout_id": workout_id
#         },
#         str(current_user.id)
#     )


@router.get("/posts/{post_id}", response_model=Dict)
async def get_post_endpoint(
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
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return post


@router.delete("/posts/{post_id}", response_model=bool)
async def delete_post_endpoint(
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
    post = await get_post_by_id(post_id)
    print(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Check if the post belongs to the current user
    if str(post['user_id']) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_post(post_id)
    return result


@router.post("/posts/{post_id}/like", response_model=Dict)
async def like_post_endpoint(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Like a post.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        Updated post with like count
    """
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    updated_post = await like_post_db(post_id, str(current_user.id))
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not like post",
        )
    
    return updated_post


@router.post("/posts/{post_id}/unlike", response_model=Dict)
async def unlike_post_endpoint(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Unlike a post.
    
    Args:
        post_id: Post ID
        current_user: Current authenticated user
        
    Returns:
        Updated post with like count
    """
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    updated_post = await unlike_post_db(post_id, str(current_user.id))
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not unlike post",
        )
    
    return updated_post


@router.post("/posts/{post_id}/comments", response_model=Dict)
async def add_comment_endpoint(
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
        Added comment
    """
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    comment = await add_comment(
        post_id, 
        {"content": content},
        str(current_user.id)
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add comment",
        )
    
    return comment


@router.get("/posts/{post_id}/comments", response_model=List[Dict])
async def get_comments_endpoint(
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
    post = await get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return await get_comments(post_id, skip, limit)


@router.get("/user/posts", response_model=List[Dict])
async def get_current_user_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's posts.
    
    Args:
        skip: Number of posts to skip
        limit: Maximum number of posts to return
        current_user: Current authenticated user
        
    Returns:
        List of posts
    """
    return await get_user_posts(str(current_user.id), skip, limit)


@router.get("/user/{user_id}/posts", response_model=List[Dict])
async def get_user_posts_endpoint(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a user's posts.
    
    Args:
        user_id: User ID
        skip: Number of posts to skip
        limit: Maximum number of posts to return
        current_user: Current authenticated user
        
    Returns:
        List of posts
    """
    return await get_user_posts(user_id, skip, limit)


@router.post("/follow/{user_id}", response_model=bool)
async def follow_user_endpoint(
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
    
    result = await follow_user_db(str(current_user.id), user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not follow user",
        )
    
    return result


@router.post("/unfollow/{user_id}", response_model=bool)
async def unfollow_user_endpoint(
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
    
    result = await unfollow_user_db(str(current_user.id), user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not unfollow user",
        )
    
    return result


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


@router.get("/search")
async def search(
    q: str,
    collection: str = "social_posts",
    skip: int = 0,
    limit: int = 20
):
    """Search for content across the platform"""
    results = await search_content(q, collection, limit, skip)
    return results

