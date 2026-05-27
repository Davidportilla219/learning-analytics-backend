"""
Health models for the Academic Risk Service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime


class DatabaseHealth(BaseModel):
    """Database health response model."""
    status: str
    database_name: str
    timestamp: datetime
    message: str


class RiskAssessment(BaseModel):
    """Risk assessment response model."""
    user_id: str
    risk_score: float
    risk_level: str
    risk_factors: list
    recommendations: list
    assessment_timestamp: datetime
    course_id: Optional[str] = None
    semester: Optional[str] = None


class UserRiskProfile(BaseModel):
    """User risk profile model."""
    user_id: str
    overall_risk_score: float
    overall_risk_level: str
    risk_history: list
    last_assessment: datetime
    courses_at_risk: list
    intervention_needed: bool


class RiskAlert(BaseModel):
    """Risk alert model."""
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