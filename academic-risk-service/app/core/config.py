"""
Configuration settings for the Academic Risk Service.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings for Academic Risk Service."""
    
    # Service configuration
    SERVICE_NAME: str = "academic-risk-service"
    PORT: int = 8004
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
    DB_NAME: str = "academic_risk_db"
    
    # RabbitMQ configuration
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_EXCHANGE: str = "risk_events"
    RABBITMQ_QUEUE: str = "risk_assessments"
    RABBITMQ_ROUTING_KEY: str = "risk_assessments"
    
    # Risk prediction configuration
    RISK_MODEL_PATH: str = "/app/models/risk_model.pkl"
    RISK_THRESHOLD_LOW: float = 0.3
    RISK_THRESHOLD_MEDIUM: float = 0.6
    RISK_THRESHOLD_HIGH: float = 0.8
    
    # Academic risk factors
    MIN_LOGIN_THRESHOLD: int = 5
    MIN_ASSIGNMENT_THRESHOLD: int = 3
    MIN_FORUM_THRESHOLD: int = 2
    MIN_VIDEO_THRESHOLD: int = 1
    MIN_ASSESSMENT_THRESHOLD: int = 1
    
    # Alert configuration
    ALERT_COOLDOWN_HOURS: int = 24
    MAX_ALERTS_PER_USER: int = 5
    
    # Processing configuration
    MAX_EVENTS_PER_BATCH: int = 1000
    PROCESSING_TIMEOUT: int = 60
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()