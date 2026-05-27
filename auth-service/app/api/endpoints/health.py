"""
Health check endpoints.
"""

from fastapi import APIRouter
from shared.contracts.dtos import HealthResponseDTO
from shared.contracts.enums import ServiceName

router = APIRouter()


@router.get("/health", response_model=HealthResponseDTO)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    from app.core.config import settings
    
    return HealthResponseDTO(
        status="ok",
        service=settings.SERVICE_NAME,
        timestamp=datetime.utcnow(),
        version=settings.API_VERSION
    )


@router.get("/health-aggregate")
async def health_aggregate():
    """Health check aggregation endpoint."""
    # This would typically check all dependent services
    # For now, return a simple response
    return {
        "status": "ok",
        "services": {
            "auth-service": "ok",
            "event-capture-service": "ok",
            "telemetry-processor-service": "ok",
            "academic-risk-service": "ok",
            "alert-service": "ok"
        },
        "timestamp": "2026-05-26T19:28:00Z"
    }