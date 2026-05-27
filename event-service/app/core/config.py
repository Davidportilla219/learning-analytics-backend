"""
Configuration module for the Event Capture Service.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "event-capture-service"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "event_service_db"
    DATABASE_URL: str = ""
    
    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_QUEUE: str = "learning_events"
    RABBITMQ_EXCHANGE: str = "learning_events"
    
    # JWT settings
    JWT_SECRET: str = "your-secret-key-change-in-production-please-use-a-secure-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # Event processing settings
    MAX_EVENT_SIZE: int = 1024 * 1024  # 1MB
    BATCH_SIZE: int = 100
    PROCESSING_TIMEOUT: int = 30  # seconds
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Development settings
    DEBUG: bool = True
    RELOAD: bool = True
    
    class Config:
        env_file = "../.env"
        case_sensitive = True


# Create settings instance
settings = Settings()

if not settings.DATABASE_URL:
    settings.DATABASE_URL = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
