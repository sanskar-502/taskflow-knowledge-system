"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the application."""

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/taskflow_db"

    # JWT Authentication
    SECRET_KEY: str = "change-this-to-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Application
    APP_NAME: str = "TaskFlow AI"
    DEBUG: bool = True

    # File uploads
    UPLOAD_DIR: str = "uploads"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "chroma_data"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached instance of Settings.
    Using lru_cache so we only read the .env file once.
    """
    return Settings()
