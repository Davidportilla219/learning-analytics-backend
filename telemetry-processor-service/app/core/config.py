"""
Configuration settings for the Telemetry Processor Service.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings for Telemetry Processor Service."""
    
    # Service configuration
    SERVICE_NAME: str = "telemetry-processor-service"
    PORT: int = 8003
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # CORS configuration
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Database configuration
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "telemetry_processor_db"
    
    # RabbitMQ configuration
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_EXCHANGE: str = "learning_events"
    RABBITMQ_QUEUE: str = "processed_events"
    RABBITMQ_ROUTING_KEY: str = "processed_events"
    
    # Event processing configuration
    MAX_EVENT_SIZE: int = 1048576  # 1MB
    BATCH_SIZE: int = 100
    PROCESSING_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5
    
    # Risk prediction configuration
    RISK_THRESHOLD_LOW: float = 0.3
    RISK_THRESHOLD_MEDIUM: float = 0.6
    RISK_THRESHOLD_HIGH: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()