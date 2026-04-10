"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Agentic RAG Enterprise AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # LLM Configuration
    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API Key")
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Vector Store
    VECTOR_STORE_PATH: str = "./data/vector_store"
    VECTOR_STORE_TYPE: str = "faiss"

    # Document Processing
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE_MB: int = 50
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Memory
    MEMORY_TYPE: str = "in_memory"
    MAX_MEMORY_ITEMS: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production-use-strong-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
