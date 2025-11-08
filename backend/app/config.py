"""
Configuration management for the AI TA Platform.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./ai_ta_platform.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Claude API
    ANTHROPIC_API_KEY: str

    # App
    UPLOADS_DIR: str = "./uploads"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
