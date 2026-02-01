"""
Configuration management for AI Safety Platform

Environment-based configuration with validation.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

# Find project root (config.py is at backend/app/core/config.py, so 3 levels up = AI-safety/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Explicitly load .env
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "IntellectSafe"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3002"], env="CORS_ORIGINS")

    # Database
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")

    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_QUEUE_DB: int = 1
    REDIS_CACHE_DB: int = 2
    REDIS_RATE_LIMIT_DB: int = 3

    # LLM Providers
    GEMINI_API_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("GEMINI_API_KEY"))
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT: int = 30

    GROQ_API_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("GROQ_API_KEY", "GROK_API_KEY"))
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TIMEOUT: int = 30

    GEMINI2_API_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("GEMINI2_API_KEY"))
    GEMINI2_MODEL: str = "gemini-2.5-flash"
    GEMINI2_TIMEOUT: int = 30

    GROK2_API_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("GROK2_API_KEY"))
    GROK2_MODEL: str = "llama-3.3-70b-versatile"
    GROK2_TIMEOUT: int = 30

    OPENROUTER_API_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("OPEN_ROUTER_KEY", "OPENROUTER_API_KEY"))
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    OPENROUTER_TIMEOUT: int = 30

    # LLM Council
    COUNCIL_TIMEOUT: int = 60  # Max time for council decision
    COUNCIL_MIN_CONSENSUS: float = 0.6  # Minimum consensus for decision
    COUNCIL_ENABLE_PARALLEL: bool = True  # Parallel model calls
    COUNCIL_MAX_RETRIES: int = 2

    # Safety Thresholds
    RISK_THRESHOLD_BLOCK: float = 70.0  # Block if score >= 70
    RISK_THRESHOLD_FLAG: float = 40.0  # Flag if score >= 40
    CONFIDENCE_THRESHOLD: float = 0.7  # Minimum confidence for action

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Security
    SECRET_KEY: Optional[str] = Field(None, env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_HEADER: str = "X-API-Key"

    # Audit
    AUDIT_RETENTION_DAYS: int = 365
    AUDIT_IMMUTABLE: bool = True

    # Workers
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # MCP
    MCP_ENABLED: bool = True
    MCP_PORT: int = 8001
    MCP_REQUIRE_AUTH: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
