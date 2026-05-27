"""
Health models for the Telemetry Processor Service.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional

Base = declarative_base()


class HealthRecord(Base):
    """Database model for health checks."""
    
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default="now()")
    details = Column(Text, nullable=True)


class HealthResponseDTO(BaseModel):
    """DTO for health check responses."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field("1.0.0", description="Service version")
    
    class Config:
        from_attributes = True


class ProcessedEvent(BaseModel):
    """DTO for processed events."""
    
    event_id: str
    original_event_type: str
    processed_event_type: str
    user_id: str
    course_id: Optional[str]
    timestamp: datetime
    processed_data: dict
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    processing_time: float
    errors: Optional[list] = None
    
    class Config:
        from_attributes = True


class ProcessingStats(BaseModel):
    """DTO for processing statistics."""
    
    total_processed: int
    success_rate: float
    average_processing_time: float
    error_count: int
    risk_distribution: dict
    
    class Config:
        from_attributes = True