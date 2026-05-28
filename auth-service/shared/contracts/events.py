"""
Event schemas for the Learning Analytics Platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class EventType(str, Enum):
    """Educational event types."""
    EXERCISE_SUBMITTED = "exercise_submitted"
    QUIZ_COMPLETED = "quiz_completed"
    VIDEO_WATCHED = "video_watched"
    FORUM_POST = "forum_post"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    LOGIN = "login"
    LOGOUT = "logout"
    COURSE_ENROLLED = "course_enrolled"
    COURSE_COMPLETED = "course_completed"


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EventTypes:
    """Event type constants."""
    EXERCISE_SUBMITTED = EventType.EXERCISE_SUBMITTED
    QUIZ_COMPLETED = EventType.QUIZ_COMPLETED
    VIDEO_WATCHED = EventType.VIDEO_WATCHED
    FORUM_POST = EventType.FORUM_POST
    ASSIGNMENT_SUBMITTED = EventType.ASSIGNMENT_SUBMITTED
    LOGIN = EventType.LOGIN
    LOGOUT = EventType.LOGOUT
    COURSE_ENROLLED = EventType.COURSE_ENROLLED
    COURSE_COMPLETED = EventType.COURSE_COMPLETED


class RiskLevels:
    """Risk level constants."""
    LOW = RiskLevel.LOW
    MEDIUM = RiskLevel.MEDIUM
    HIGH = RiskLevel.HIGH


class BaseEvent(BaseModel):
    """Base event schema for all educational events."""
    
    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of educational event")
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    institution_id: str = Field(..., description="Institution identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    
    @validator('event_id')
    def validate_event_id(cls, v):
        if v is None:
            return uuid4()
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        if v is None:
            return datetime.utcnow()
        return v


class ProcessedEvent(BaseModel):
    """Processed telemetry event schema."""
    
    event_id: UUID = Field(..., description="Original event identifier")
    student_id: str = Field(..., description="Student identifier")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="Engagement score (0-1)")
    activity_count: int = Field(..., ge=0, description="Total activity count")
    failed_attempts: int = Field(..., ge=0, description="Number of failed attempts")
    inactivity_days: int = Field(..., ge=0, description="Days of inactivity")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    
    @validator('engagement_score')
    def validate_engagement_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Engagement score must be between 0.0 and 1.0')
        return v


class RiskAlert(BaseModel):
    """Risk alert schema for academic risk predictions."""
    
    alert_id: UUID = Field(default_factory=uuid4, description="Unique alert identifier")
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    reason: str = Field(..., description="Reason for risk assessment")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation timestamp")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    
    @validator('alert_id')
    def validate_alert_id(cls, v):
        if v is None:
            return uuid4()
        return v


class EventValidationResult(BaseModel):
    """Result of event validation."""
    
    is_valid: bool = Field(..., description="Whether the event is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")