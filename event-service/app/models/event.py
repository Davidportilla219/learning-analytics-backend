"""
Event models for the Event Capture Service.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
import json

Base = declarative_base()


class Event(Base):
    """Database model for learning analytics events."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    course_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Add indexes for better query performance
    __table_args__ = (
        Index('idx_events_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_events_course_timestamp', 'course_id', 'timestamp'),
        Index('idx_events_session_timestamp', 'session_id', 'timestamp'),
    )


class EventCreate(BaseModel):
    """Schema for creating new events."""
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of event (login, page_view, assignment_submit, etc.)")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    course_id: Optional[str] = Field(None, description="Course identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    event_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Validate event type."""
        allowed_types = [
            'login', 'logout', 'page_view', 'video_play', 'video_pause',
            'assignment_view', 'assignment_submit', 'quiz_start', 'quiz_submit',
            'forum_post', 'forum_reply', 'resource_download', 'search',
            'navigation', 'assessment', 'completion'
        ]
        if v not in allowed_types:
            raise ValueError(f"Invalid event type: {v}")
        return v
    
    @validator('data')
    def validate_data(cls, v):
        """Validate event data."""
        if not isinstance(v, dict):
            raise ValueError("Event data must be a dictionary")
        
        # Validate data size (max 1MB)
        data_str = json.dumps(v)
        if len(data_str) > 1024 * 1024:  # 1MB
            raise ValueError("Event data too large (max 1MB)")
        
        return v


class EventUpdate(BaseModel):
    """Schema for updating events."""
    
    event_type: Optional[str] = Field(None, description="Type of event")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    course_id: Optional[str] = Field(None, description="Course identifier")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Event data")
    event_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class EventResponse(BaseModel):
    """Schema for event responses."""
    
    id: int
    event_id: str
    event_type: str
    user_id: str
    session_id: Optional[str]
    course_id: Optional[str]
    timestamp: datetime
    data: Dict[str, Any]
    event_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EventBatch(BaseModel):
    """Schema for batch event creation."""
    
    events: List[EventCreate] = Field(..., description="List of events to create")


class EventBatchResponse(BaseModel):
    """Schema for batch event response."""
    
    created_count: int = Field(..., description="Number of events created")
    failed_events: List[Dict[str, Any]] = Field(default_factory=list, description="List of failed events")
    errors: List[str] = Field(default_factory=list, description="List of error messages")


class EventStats(BaseModel):
    """Schema for event statistics."""
    
    total_events: int
    unique_users: int
    event_types: Dict[str, int]
    time_range: Dict[str, datetime]
    avg_events_per_user: float