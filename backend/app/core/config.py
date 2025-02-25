from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings.
    
    These settings are loaded from environment variables and .env file.
    """
    PROJECT_NAME: str = "Dumbbell Diaries API"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Settings
    MONGODB_URI: str = Field(..., env="MONGODB_URI")
    MONGODB_DB_NAME: str = "dumbbell_diaries"
    
    # JWT Settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Elasticsearch Settings
    # ELASTICSEARCH_URI: str = Field(..., env="ELASTICSEARCH_URI")
    
    # Firebase Settings
    FIREBASE_CREDENTIALS: str = Field(..., env="FIREBASE_CREDENTIALS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
