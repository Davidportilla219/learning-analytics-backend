"""
Data Transfer Objects (DTOs) for the Learning Analytics Platform.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class EventSubmissionDTO(BaseModel):
    """DTO for event submission requests."""
    
    event_type: str = Field(..., description="Type of educational event")
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    institution_id: str = Field(..., description="Institution identifier")
    payload: dict = Field(default_factory=dict, description="Event-specific data")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")


class RiskPredictionDTO(BaseModel):
    """DTO for risk prediction requests."""
    
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="Engagement score")
    activity_count: int = Field(..., ge=0, description="Activity count")
    failed_attempts: int = Field(..., ge=0, description="Failed attempts")
    inactivity_days: int = Field(..., ge=0, description="Inactivity days")


class AlertResponseDTO(BaseModel):
    """DTO for alert responses."""
    
    alert_id: UUID = Field(..., description="Alert identifier")
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    risk_level: str = Field(..., description="Risk level")
    reason: str = Field(..., description="Risk reason")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")


class HealthResponseDTO(BaseModel):
    """DTO for health check responses."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field("1.0.0", description="Service version")


class AuthRequestDTO(BaseModel):
    """DTO for authentication requests."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password")


class AuthResponseDTO(BaseModel):
    """DTO for authentication responses."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(1800, description="Token expiration time in seconds")


class UserCreateDTO(BaseModel):
    """DTO for user creation requests."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    is_superuser: bool = Field(default=False, description="Superuser flag")


class UserResponseDTO(BaseModel):
    """DTO for user responses."""

    id: UUID
    username: str
    name: Optional[str] = None
    email: str
    role: str = "student"
    is_superuser: bool
    institution: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True