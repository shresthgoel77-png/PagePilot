from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchOS API"

    # Required exact fields that cause fast-fail on missing variable
    DATABASE_URL: str = Field(..., description="Primary PostgreSQL Database URL")
    QDRANT_URL: str = Field(..., description="Vector database Qdrant URL")
    SECRET_KEY: str = Field(..., description="JWT Auth Secret Key")
    UPLOAD_DIR: str = Field(..., description="Local PDF Upload Directory")
    GEMINI_API_KEY: str = Field(..., description="Gemini LLM Key")

    # Chunking Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Security & Networking
    FRONTEND_URLS: List[str] = ["http://localhost:3000"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BYPASS_CLERK: bool = False

    # We read from .env if present
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
