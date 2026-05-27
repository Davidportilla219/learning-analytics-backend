"""
Models for the Alert Service.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime


class Alert(BaseModel):
    """Alert model."""
    alert_id: str
    user_id: str
    risk_score: float
    risk_level: str
    alert_type: str
    message: str
    timestamp: datetime
    course_id: Optional[str] = None
    instructor_id: Optional[str] = None
    acknowledged: bool = False
    resolved: bool = False


class AlertResponse(BaseModel):
    """Alert response model."""
    alert_id: str
    user_id: str
    risk_score: float
    risk_level: str
    alert_type: str
    message: str
    timestamp: datetime
    course_id: Optional[str] = None
    instructor_id: Optional[str] = None
    acknowledged: bool
    resolved: bool
    created_at: datetime
