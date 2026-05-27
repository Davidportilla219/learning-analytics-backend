"""
Health check endpoints for the Telemetry Processor Service.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.core.config import settings
from app.models.health import HealthResponseDTO

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponseDTO)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponseDTO(
        status="ok",
        service=settings.SERVICE_NAME,
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.get("/health/database")
async def health_database(db: AsyncSession = Depends(get_db_session)):
    """Database health check endpoint."""
    try:
        # Simple query to test database connection
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@router.get("/health/rabbitmq")
async def health_rabbitmq():
    """RabbitMQ health check endpoint."""
    try:
        # TODO: Implement actual RabbitMQ connection check
        return {"status": "healthy", "rabbitmq": "connected"}
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        return {"status": "unhealthy", "rabbitmq": "disconnected", "error": str(e)}


@router.get("/health/full")
async def health_full(db: AsyncSession = Depends(get_db_session)):
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
    
    # Check RabbitMQ
    try:
        # TODO: Implement actual RabbitMQ connection check
        health_status["checks"]["rabbitmq"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["rabbitmq"] = f"unhealthy: {str(e)}"
    
    return health_status