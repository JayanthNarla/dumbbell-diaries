from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.models.social import PostCreate, PostUpdate, PostInDB, CommentCreate, CommentInDB
from app.db.mongodb.mongodb import get_database
from app.db.mongodb.search import sync_post


# async def create_post(post: PostCreate, user_id: str) -> PostInDB:
#     """
#     Create a new social post.
    
#     Args:
#         post: Post data
#         user_id: User ID
        
#     Returns:
#         Created post
#     """
#     db = await get_database()
    
#     post_in_db = PostInDB(
#         **post,
#         user_id=ObjectId(user_id),
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow(),
#         likes=[],
#         comments=[],
#         likes_count=0,
#         comments_count=0
#     )
    
#     result = await db.posts.insert_one(post_in_db.dict(by_alias=True))
#     post_in_db.id = result.inserted_id
    
#     # Index in Elasticsearch
#     await sync_post(post_in_db.dict(by_alias=True))
    
#     return post_in_db
async def create_post(post: PostCreate, user_id: str) -> PostInDB:
    db = await get_database()
    
    # Generate a new ObjectId for the post
    post_id = ObjectId()
    
    # Prepare data for MongoDB (uses ObjectIds)
    mongo_data = {
        "_id": post_id,
        "user_id": ObjectId(user_id),  # Convert to ObjectId for DB
        **post.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "likes": [],
        "comments_count": 0,
        "likes_count": 0
    }
    
    # Insert into MongoDB
    await db.social_posts.insert_one(mongo_data)
    
    # Create response model with string IDs
    post_in_db = PostInDB(
        id=(post_id),
        user_id=ObjectId(user_id),  # Keep as original string
        **post.dict(),
        created_at=mongo_data["created_at"],
        updated_at=mongo_data["updated_at"],
        likes=[],
        comments_count=0,
        likes_count=0
    )
    
    await sync_post(post_in_db.dict(by_alias=True))
    return post_in_db.dict(by_alias=True)


async def get_post_by_id(post_id: str) -> Optional[PostInDB]:
    """
    Get a post by ID.
    
    Args:
        post_id: Post ID
        
    Returns:
        Post or None if not found
    """
    db = await get_database()
    
    post_data = await db.social_posts.find_one({"_id": ObjectId(post_id)})
    if post_data:
        return PostInDB(**post_data).dict(by_alias=True)
    
    return None


async def update_post(post_id: str, post_update: PostUpdate) -> Optional[PostInDB]:
    """
    Update a post.
    
    Args:
        post_id: Post ID
        post_update: Post update data
        
    Returns:
        Updated post or None if not found
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in post_update.dict().items() if v is not None}
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the post
    result = await db.social_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated post
        updated_post = await get_post_by_id(post_id)
        
        # Update in Elasticsearch
        if updated_post:
            await sync_post(updated_post.dict(by_alias=True), operation="update")
            
        return updated_post
    
    return None


async def delete_post(post_id: str) -> bool:
    """
    Delete a post.
    
    Args:
        post_id: Post ID
        
    Returns:
        True if post was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.social_posts.delete_one({"_id": ObjectId(post_id)})
    
    # Delete from Elasticsearch
    if result.deleted_count:
        await sync_post({"_id": post_id}, operation="delete")
        
    return result.deleted_count > 0


async def like_post(post_id: str, user_id: str) -> Optional[PostInDB]:
    """
    Like a post.
    
    Args:
        post_id: Post ID
        user_id: User ID who is liking
        
    Returns:
        Updated post or None if not found
    """
    db = await get_database()
    
    # Only add the like if the user hasn't already liked the post
    result = await db.social_posts.update_one(
        {
            "_id": ObjectId(post_id),
            "likes": {"$ne": ObjectId(user_id)}
        },
        {
            "$addToSet": {"likes": ObjectId(user_id)},
            "$inc": {"likes_count": 1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count:
        # Get the updated post
        updated_post = await get_post_by_id((post_id))
        
        # Update in Elasticsearch
        if updated_post:
            await sync_post(updated_post.dict(by_alias=True), operation="update")
            
        return updated_post
    
    # Post might exist but user already liked it
    existing_post = await get_post_by_id((post_id))
    return existing_post


async def unlike_post(post_id: str, user_id: str) -> Optional[PostInDB]:
    """
    Unlike a post.
    
    Args:
        post_id: Post ID
        user_id: User ID who is unliking
        
    Returns:
        Updated post or None if not found
    """
    db = await get_database()
    
    # Only remove the like if the user has liked the post
    result = await db.social_posts.update_one(
        {
            "_id": ObjectId(post_id),
            "likes": ObjectId(user_id)
        },
        {
            "$pull": {"likes": ObjectId(user_id)},
            "$inc": {"likes_count": -1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count:
        # Get the updated post
        updated_post = await get_post_by_id(post_id)
        
        # Update in Elasticsearch
        if updated_post:
            await sync_post(updated_post, operation="update")
            
        return updated_post
    
    # Post might exist but user hasn't liked it
    existing_post = await get_post_by_id(post_id)
    return existing_post


async def add_comment(post_id: str, comment: CommentCreate, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Add a comment to a post.
    
    Args:
        post_id: Post ID
        comment: Comment data
        user_id: User ID who is commenting
        
    Returns:
        Created comment or None if post not found
    """
    db = await get_database()
    
    comment_id = ObjectId()
    comment_data = {
        "_id": comment_id,
        "post_id": ObjectId(post_id),
        "user_id": ObjectId(user_id),
        "content": comment['content'],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "likes": [],
        "likes_count": 0
    }
    
    # First check if post exists
    post = await get_post_by_id(post_id)
    if not post:
        return None
    
    # Insert comment into comments collection
    await db.comments.insert_one(comment_data)
    
    # Update post to increment comment count
    await db.social_posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$inc": {"comments_count": 1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Update in Elasticsearch
    post = await get_post_by_id(post_id)
    if post:
        await sync_post(post, operation="update")
    
    # Convert ObjectId to string
    comment_data["_id"] = str(comment_data["_id"])
    comment_data["post_id"] = str(comment_data["post_id"])
    comment_data["user_id"] = str(comment_data["user_id"])
    
    return comment_data


async def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_direction: int = -1
) -> List[Dict[str, Any]]:
    """
    Get comments for a post.
    
    Args:
        post_id: Post ID
        skip: Number of comments to skip
        limit: Maximum number of comments to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of comments with user info
    """
    db = await get_database()
    
    # Aggregate to get comments with user info
    pipeline = [
        {"$match": {"post_id": ObjectId(post_id)}},
        {"$sort": {sort_by: sort_direction}},
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
                "_id": 1,
                "post_id": 1,
                "user_id": 1,
                "content": 1,
                "created_at": 1,
                "updated_at": 1,
                "likes_count": 1,
                "user_name": "$user.username",
                "user_profile_picture": "$user.profile_picture"
            }
        }
    ]
    
    comments = []
    cursor = db.comments.aggregate(pipeline)
    
    async for comment in cursor:
        # Convert ObjectId to string
        comment["_id"] = str(comment["_id"])
        comment["post_id"] = str(comment["post_id"])
        comment["user_id"] = str(comment["user_id"])
        comments.append(comment)
    
    return comments


async def follow_user(follower_id: str, followee_id: str) -> bool:
    """
    Follow a user.
    
    Args:
        follower_id: User ID who is following
        followee_id: User ID who is being followed
        
    Returns:
        True if successfully followed, False otherwise
    """
    db = await get_database()
    
    # Check if users exist
    follower = await db.users.find_one({"_id": ObjectId(follower_id)})
    followee = await db.users.find_one({"_id": ObjectId(followee_id)})
    
    if not follower or not followee:
        return False
    
    # Add to follows collection
    result = await db.follows.update_one(
        {
            "follower_id": ObjectId(follower_id),
            "followee_id": ObjectId(followee_id)
        },
        {
            "$setOnInsert": {
                "follower_id": ObjectId(follower_id),
                "followee_id": ObjectId(followee_id),
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Update follower's following count
    await db.users.update_one(
        {"_id": ObjectId(follower_id)},
        {"$inc": {"following_count": 1 if result.upserted_id else 0}}
    )
    
    # Update followee's followers count
    await db.users.update_one(
        {"_id": ObjectId(followee_id)},
        {"$inc": {"followers_count": 1 if result.upserted_id else 0}}
    )
    
    return True


async def unfollow_user(follower_id: str, followee_id: str) -> bool:
    """
    Unfollow a user.
    
    Args:
        follower_id: User ID who is unfollowing
        followee_id: User ID who is being unfollowed
        
    Returns:
        True if successfully unfollowed, False otherwise
    """
    db = await get_database()
    
    # Remove from follows collection
    result = await db.follows.delete_one({
        "follower_id": ObjectId(follower_id),
        "followee_id": ObjectId(followee_id)
    })
    
    if result.deleted_count:
        # Update follower's following count
        await db.users.update_one(
            {"_id": ObjectId(follower_id)},
            {"$inc": {"following_count": -1}}
        )
        
        # Update followee's followers count
        await db.users.update_one(
            {"_id": ObjectId(followee_id)},
            {"$inc": {"followers_count": -1}}
        )
    
    return result.deleted_count > 0


async def get_social_feed(
    user_id: str,
    feed_type: str = "following",
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get a user's social feed.
    
    Args:
        user_id: User ID
        feed_type: Type of feed ('following' or 'discover')
        skip: Number of posts to skip
        limit: Maximum number of posts to return
        
    Returns:
        List of posts with user info
    """
    db = await get_database()
    
    if feed_type == "following":
        # Get IDs of users the current user is following
        follows = db.follows.find({"follower_id": ObjectId(user_id)})
        following_ids = []
        
        async for follow in follows:
            following_ids.append(follow["followee_id"])
        
        # Include the user's own posts
        following_ids.append(ObjectId(user_id))
        
        # Get posts from followed users
        pipeline = [
            {"$match": {"user_id": {"$in": following_ids}}},
            {"$sort": {"created_at": -1}},
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
                    "_id": 1,
                    "user_id": 1,
                    "content": 1,
                    "media_urls": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "likes_count": 1,
                    "comments_count": 1,
                    "user_name": "$user.username",
                    "user_profile_picture": "$user.profile_picture"
                }
            }
        ]
    else:  # discover feed
        # Get posts from all users (could add more sophisticated discovery logic)
        pipeline = [
            {"$sort": {"likes_count": -1, "created_at": -1}},
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
                    "_id": 1,
                    "user_id": 1,
                    "content": 1,
                    "media_urls": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "likes_count": 1,
                    "comments_count": 1,
                    "user_name": "$user.username",
                    "user_profile_picture": "$user.profile_picture"
                }
            }
        ]
    
    posts = []
    cursor = db.social_posts.aggregate(pipeline)
    
    async for post in cursor:
        # Convert ObjectId to string
        post["_id"] = str(post["_id"])
        post["user_id"] = str(post["user_id"])
        posts.append(post)
    
    return posts


async def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get a user's posts.
    
    Args:
        user_id: User ID
        skip: Number of posts to skip
        limit: Maximum number of posts to return
        
    Returns:
        List of posts
    """
    db = await get_database()
    
    # Aggregate to get posts with user info
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$sort": {"created_at": -1}},
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
                "_id": 1,
                "user_id": 1,
                "content": 1,
                "media_urls": 1,
                "created_at": 1,
                "updated_at": 1,
                "likes_count": 1,
                "comments_count": 1,
                "user_name": "$user.username",
                "user_profile_picture": "$user.profile_picture"
            }
        }
    ]
    
    posts = []
    cursor = db.social_posts.aggregate(pipeline)
    
    async for post in cursor:
        # Convert ObjectId to string
        post["_id"] = str(post["_id"])
        post["user_id"] = str(post["user_id"])
        posts.append(post)
    
    return posts 