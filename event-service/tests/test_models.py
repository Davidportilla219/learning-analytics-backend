"""
Test suite for the Event Service models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.event import (
    EventCreate, EventUpdate, EventResponse, 
    EventBatch, EventBatchResponse, EventStats,
    Event
)


class TestEventCreate:
    """Test suite for EventCreate model."""
    
    def test_valid_event_create(self):
        """Test creating a valid EventCreate."""
        event_data = {
            "event_id": "test-event-001",
            "event_type": "login",
            "user_id": "user-001",
            "timestamp": datetime.now(),
            "data": {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        }
        
        event = EventCreate(**event_data)
        assert event.event_id == "test-event-001"
        assert event.event_type == "login"
        assert event.user_id == "user-001"
        assert event.data == {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        assert event.session_id is None
        assert event.course_id is None
        assert event.metadata is None
    
    def test_event_create_with_optional_fields(self):
        """Test creating EventCreate with optional fields."""
        event_data = {
            "event_id": "test-event-002",
            "event_type": "page_view",
            "user_id": "user-001",
            "session_id": "session-001",
            "course_id": "course-001",
            "timestamp": datetime.now(),
            "data": {"page": "/dashboard"},
            "metadata": {"device": "desktop", "browser": "chrome"}
        }
        
        event = EventCreate(**event_data)
        assert event.session_id == "session-001"
        assert event.course_id == "course-001"
        assert event.metadata == {"device": "desktop", "browser": "chrome"}
    
    def test_invalid_event_type(self):
        """Test EventCreate with invalid event type."""
        event_data = {
            "event_id": "test-event-003",
            "event_type": "invalid_type",
            "user_id": "user-001",
            "timestamp": datetime.now(),
            "data": {"test": "data"}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(**event_data)
        
        assert "Invalid event type" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test EventCreate with missing required fields."""
        event_data = {
            "event_id": "test-event-004",
            # Missing event_type, user_id, timestamp, data
        }
        
        with pytest.raises(ValidationError):
            EventCreate(**event_data)
    
    def test_event_data_too_large(self):
        """Test EventCreate with data that's too large."""
        large_data = {"data": "x" * (1024 * 1024 + 1)}  # 1MB + 1 byte
        
        event_data = {
            "event_id": "test-event-005",
            "event_type": "login",
            "user_id": "user-001",
            "timestamp": datetime.now(),
            "data": large_data
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(**event_data)
        
        assert "Event data too large" in str(exc_info.value)
    
    def test_invalid_data_type(self):
        """Test EventCreate with invalid data type."""
        event_data = {
            "event_id": "test-event-006",
            "event_type": "login",
            "user_id": "user-001",
            "timestamp": datetime.now(),
            "data": "invalid_data_string"  # Should be dict, not string
        }
        
        with pytest.raises(ValidationError):
            EventCreate(**event_data)


class TestEventUpdate:
    """Test suite for EventUpdate model."""
    
    def test_valid_event_update(self):
        """Test creating a valid EventUpdate."""
        update_data = {
            "event_type": "logout",
            "user_id": "user-updated",
            "metadata": {"updated": True}
        }
        
        update = EventUpdate(**update_data)
        assert update.event_type == "logout"
        assert update.user_id == "user-updated"
        assert update.metadata == {"updated": True}
        assert update.session_id is None
        assert update.course_id is None
        assert update.timestamp is None
        assert update.data is None
    
    def test_event_update_with_partial_data(self):
        """Test EventUpdate with partial data."""
        update_data = {
            "session_id": "session-updated"
        }
        
        update = EventUpdate(**update_data)
        assert update.session_id == "session-updated"
        assert update.event_type is None
        assert update.user_id is None
    
    def test_empty_event_update(self):
        """Test EventUpdate with no data."""
        update = EventUpdate()
        assert update.event_type is None
        assert update.user_id is None
        assert update.session_id is None
        assert update.course_id is None
        assert update.timestamp is None
        assert update.data is None
        assert update.metadata is None


class TestEventResponse:
    """Test suite for EventResponse model."""
    
    def test_valid_event_response(self):
        """Test creating a valid EventResponse."""
        response_data = {
            "id": 1,
            "event_id": "test-event-001",
            "event_type": "login",
            "user_id": "user-001",
            "session_id": "session-001",
            "course_id": "course-001",
            "timestamp": datetime.now(),
            "data": {"ip_address": "192.168.1.1"},
            "metadata": {"device": "desktop"},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        response = EventResponse(**response_data)
        assert response.id == 1
        assert response.event_id == "test-event-001"
        assert response.event_type == "login"
        assert response.user_id == "user-001"
        assert response.session_id == "session-001"
        assert response.course_id == "course-001"
        assert response.data == {"ip_address": "192.168.1.1"}
        assert response.metadata == {"device": "desktop"}
        assert response.created_at == response_data["created_at"]
        assert response.updated_at == response_data["updated_at"]


class TestEventBatch:
    """Test suite for EventBatch model."""
    
    def test_valid_event_batch(self):
        """Test creating a valid EventBatch."""
        events = [
            EventCreate(
                event_id="batch-event-001",
                event_type="login",
                user_id="user-001",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.1"}
            ),
            EventCreate(
                event_id="batch-event-002",
                event_type="page_view",
                user_id="user-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"}
            )
        ]
        
        batch = EventBatch(events=events)
        assert len(batch.events) == 2
        assert batch.events[0].event_id == "batch-event-001"
        assert batch.events[1].event_type == "page_view"
    
    def test_empty_event_batch(self):
        """Test EventBatch with empty events list."""
        batch = EventBatch(events=[])
        assert len(batch.events) == 0


class TestEventBatchResponse:
    """Test suite for EventBatchResponse model."""
    
    def test_valid_batch_response(self):
        """Test creating a valid EventBatchResponse."""
        response_data = {
            "created_count": 2,
            "failed_events": [
                {"event_id": "failed-event", "error": "Event already exists"}
            ],
            "errors": ["Error creating failed-event: Event already exists"]
        }
        
        response = EventBatchResponse(**response_data)
        assert response.created_count == 2
        assert len(response.failed_events) == 1
        assert response.failed_events[0]["event_id"] == "failed-event"
        assert len(response.errors) == 1
        assert "Event already exists" in response.errors[0]
    
    def test_empty_batch_response(self):
        """Test EventBatchResponse with empty data."""
        response = EventBatchResponse(created_count=0)
        assert response.created_count == 0
        assert len(response.failed_events) == 0
        assert len(response.errors) == 0


class TestEventStats:
    """Test suite for EventStats model."""
    
    def test_valid_event_stats(self):
        """Test creating valid EventStats."""
        stats_data = {
            "total_events": 100,
            "unique_users": 25,
            "event_types": {
                "login": 30,
                "page_view": 70
            },
            "time_range": {
                "start": datetime.now(),
                "end": datetime.now()
            },
            "avg_events_per_user": 4.0
        }
        
        stats = EventStats(**stats_data)
        assert stats.total_events == 100
        assert stats.unique_users == 25
        assert stats.event_types == {"login": 30, "page_view": 70}
        assert stats.time_range == stats_data["time_range"]
        assert stats.avg_events_per_user == 4.0
    
    def test_event_stats_zero_values(self):
        """Test EventStats with zero values."""
        stats_data = {
            "total_events": 0,
            "unique_users": 0,
            "event_types": {},
            "time_range": {"start": None, "end": None},
            "avg_events_per_user": 0.0
        }
        
        stats = EventStats(**stats_data)
        assert stats.total_events == 0
        assert stats.unique_users == 0
        assert stats.event_types == {}
        assert stats.time_range == {"start": None, "end": None}
        assert stats.avg_events_per_user == 0.0


class TestEventDatabaseModel:
    """Test suite for the Event database model."""
    
    def test_event_model_creation(self):
        """Test creating an Event database model instance."""
        event = Event(
            event_id="db-event-001",
            event_type="login",
            user_id="user-001",
            session_id="session-001",
            course_id="course-001",
            timestamp=datetime.now(),
            data={"ip_address": "192.168.1.1"},
            metadata={"device": "desktop"}
        )
        
        assert event.event_id == "db-event-001"
        assert event.event_type == "login"
        assert event.user_id == "user-001"
        assert event.session_id == "session-001"
        assert event.course_id == "course-001"
        assert event.data == {"ip_address": "192.168.1.1"}
        assert event.metadata == {"device": "desktop"}
        assert event.created_at is not None
        assert event.updated_at is not None
    
    def test_event_model_without_optional_fields(self):
        """Test creating Event without optional fields."""
        event = Event(
            event_id="db-event-002",
            event_type="page_view",
            user_id="user-002",
            timestamp=datetime.now(),
            data={"page": "/dashboard"}
        )
        
        assert event.session_id is None
        assert event.course_id is None
        assert event.metadata is None