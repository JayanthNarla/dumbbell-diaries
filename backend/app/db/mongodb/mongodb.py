from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional

async def connect_to_mongo() -> AsyncIOMotorClient:
    """
    Create a MongoDB connection pool.
    
    Returns:
        AsyncIOMotorClient: MongoDB client instance
    """
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    return mongo_client


async def close_mongo_connection(client: Optional[AsyncIOMotorClient]) -> None:
    """
    Close MongoDB connection.
    
    Args:
        client: MongoDB client instance to close
    """
    if client:
        client.close()


async def get_database():
    """
    Get MongoDB database instance.
    
    Returns:
        MongoDB database instance
    """
    from app.main import app
    return app.state.mongodb 