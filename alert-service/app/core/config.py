"""
Configuration for the Alert Service.
"""

import os
from typing import List

class Settings:
    """Settings for the Alert Service."""
    
    # Service configuration
    SERVICE_NAME = "alert-service"
    PORT = int(os.getenv("PORT", 8005))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "alert_service_db")
    
    # RabbitMQ configuration
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    # Rabbit MQ queue configuration
    ALERT_QUEUE = "risk-alerts"
    ALERT_ROUTING_KEY = "alert.risk.*"
    ALERT_EXCHANGE = "alerts"
    
    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["*"]
    
    # Notification configuration
    ALERT_RETENTION_DAYS = int(os.getenv("ALERT_RETENTION_DAYS", 30))
    BATCH_NOTIFICATION_SIZE = int(os.getenv("BATCH_NOTIFICATION_SIZE", 50))


settings = Settings()
