from typing import Callable
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from elasticsearch import AsyncElasticsearch
import firebase_admin
from firebase_admin import credentials
import os
from pathlib import Path

from app.core.config import settings
from app.db.mongodb.mongodb import close_mongo_connection, connect_to_mongo
# from app.db.elasticsearch.elasticsearch import close_elasticsearch_connection, connect_to_elasticsearch
# from app.db.elasticsearch.indices import create_indices


def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Return a function that will be executed on application startup.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Start app handler function
    """
    async def start_app() -> None:
        # Initialize MongoDB connection
        app.state.mongodb_client = await connect_to_mongo()
        app.state.mongodb = app.state.mongodb_client[settings.MONGODB_DB_NAME]
        
        # Initialize Elasticsearch connection
        # app.state.elasticsearch_client = await connect_to_elasticsearch()
        
        # Create Elasticsearch indices if they don't exist
        # await create_indices()
        
        # Initialize Firebase (if credentials are available)
        try:
            if not firebase_admin._apps:  # Check if Firebase is already initialized
                # Get the absolute path to the credentials file
                base_dir = Path(__file__).resolve().parent.parent.parent
                cred_path = os.path.join(base_dir, settings.FIREBASE_CREDENTIALS)
                
                # Check if the file exists
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized successfully")
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            # Continue without Firebase for development purposes
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Return a function that will be executed on application shutdown.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Stop app handler function
    """
    async def stop_app() -> None:
        # Close MongoDB connection
        await close_mongo_connection(app.state.mongodb_client)
        
        # Close Elasticsearch connection
        # await close_elasticsearch_connection(app.state.elasticsearch_client)
    
    return stop_app
