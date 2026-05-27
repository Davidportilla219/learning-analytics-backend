"""
Health check endpoints for the Event Capture Service.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import asyncio
import logging
import time

from app.database import get_db_session
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Event Capture Service",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@router.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(get_db_session)):
    """Database health check endpoint."""
    try:
        # Execute a simple query to test database connection
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/rabbitmq")
async def rabbitmq_health_check():
    """RabbitMQ health check endpoint."""
    try:
        # TODO: Implement actual RabbitMQ connection check
        # For now, return healthy status
        return {
            "status": "healthy",
            "rabbitmq": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "rabbitmq": "disconnected",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/full")
async def full_health_check(
    db: AsyncSession = Depends(get_db_session)
):
    """Full health check including all dependencies."""
    health_status = {
        "status": "healthy",
        "service": "Event Capture Service",
        "version": "1.0.0",
        "timestamp": time.time(),
        "dependencies": {}
    }
    
    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
    
    # Check RabbitMQ
    try:
        # TODO: Implement actual RabbitMQ connection check
        health_status["dependencies"]["rabbitmq"] = "healthy"
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["rabbitmq"] = f"unhealthy: {str(e)}"
    
    # Check service configuration
    try:
        # Check if required configuration is present
        required_configs = [
            "DATABASE_URL", "RABBITMQ_HOST", "RABBITMQ_PORT",
            "RABBITMQ_USER", "RABBITMQ_PASSWORD", "RABBITMQ_QUEUE"
        ]
        
        missing_configs = []
        for config in required_configs:
            if not getattr(settings, config, None):
                missing_configs.append(config)
        
        if missing_configs:
            health_status["status"] = "unhealthy"
            health_status["dependencies"]["configuration"] = f"missing: {missing_configs}"
        else:
            health_status["dependencies"]["configuration"] = "healthy"
            
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["configuration"] = f"unhealthy: {str(e)}"
    
    return health_status


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    """Readiness check endpoint."""
    try:
        # Check database connection
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        
        # Check if service can accept requests
        return {
            "status": "ready",
            "service": "Event Capture Service",
            "version": "1.0.0",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": time.time()
            }
        )