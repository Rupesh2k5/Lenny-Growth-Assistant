import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./lenny_growth.db",
        description="Async database connection string. Supports PostgreSQL and SQLite"
    )

    # LLM Settings
    DEFAULT_PROVIDER: str = Field(default="ollama", description="ollama | anthropic | openai | mock")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    OLLAMA_MODEL: str = Field(default="llama3.1:8b", description="Default local Ollama model")
    
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API Key")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model ID")
    
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API Key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model ID")

    # Knowledge & RAG Settings
    TRANSCRIPTS_DIR: str = Field(default="../data/transcripts", description="Path to transcript files")
    MAX_RETRIEVAL_CHUNKS: int = 1
    SIMILARITY_THRESHOLD: float = 0.15
    CHUNK_SIZE: int = 450
    CHUNK_OVERLAP: int = 50

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
