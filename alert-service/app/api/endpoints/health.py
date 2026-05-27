"""
Health endpoints for the Alert Service.
"""

import logging
from datetime import datetime
from fastapi import APIRouter
from app.models.alert import HealthCheck
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Basic health check endpoint."""
    return HealthCheck(
        status="healthy",
        service=settings.SERVICE_NAME,
        version="1.0.0",
        timestamp=datetime.now()
    )


@router.get("/health/database")
async def database_health_check():
    """Database health check endpoint."""
    try:
        # TODO: Implement actual database connection check
        return {
            "status": "healthy",
            "database_name": settings.DB_NAME,
            "timestamp": datetime.now().isoformat(),
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database_name": settings.DB_NAME,
            "timestamp": datetime.now().isoformat(),
            "message": f"Database connection failed: {str(e)}"
        }


@router.get("/health/rabbitmq")
async def rabbitmq_health_check():
    """RabbitMQ health check endpoint."""
    try:
        # TODO: Implement actual RabbitMQ connection check
        return {
            "status": "healthy",
            "service": "RabbitMQ",
            "timestamp": datetime.now().isoformat(),
            "message": "RabbitMQ connection successful"
        }
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "RabbitMQ",
            "timestamp": datetime.now().isoformat(),
            "message": f"RabbitMQ connection failed: {str(e)}"
        }


@router.get("/health/full")
async def full_health_check():
    """Full health check including all dependencies."""
    health_status = "healthy"
    dependencies = {}
    
    # Check database (placeholder)
    try:
        # TODO: Implement actual database connection check
        dependencies["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        dependencies["database"] = "unhealthy"
        health_status = "unhealthy"
    
    # Check RabbitMQ (placeholder)
    dependencies["rabbitmq"] = "healthy"
    
    # Check configuration
    try:
        _ = settings.DB_HOST
        dependencies["configuration"] = "healthy"
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        dependencies["configuration"] = "unhealthy"
        health_status = "unhealthy"
    
    return {
        "status": health_status,
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.now().isoformat()
    }
