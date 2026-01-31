"""
Configuration settings for ClipContext API.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    environment: str = "development"
    debug: bool = True
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clipcontext"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"  # Fast and good quality
    
    # Search settings
    chunk_size: int = 100  # words per chunk
    chunk_overlap: int = 20  # words overlap between chunks
    max_results: int = 5
    
    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
