"""
Test suite for the Event Capture Service API endpoints.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db_session, Base
from app.models.event import Event, EventCreate, EventResponse
from app.core.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(test_db):
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return EventCreate(
        event_id="test-event-001",
        event_type="login",
        user_id="user-001",
        session_id="session-001",
        timestamp=datetime.now(),
        data={"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
        metadata={"device": "desktop", "browser": "chrome"}
    )

class TestEventService:
    """Test suite for Event Service API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Event Capture Service"
    
    def test_database_health_endpoint(self, client):
        """Test database health endpoint."""
        response = client.get("/api/v1/health/database")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_create_event(self, client, sample_event):
        """Test creating a single event."""
        response = client.post("/api/v1/events", json=sample_event.dict())
        assert response.status_code == 201
        data = response.json()
        assert data["event_id"] == sample_event.event_id
        assert data["event_type"] == sample_event.event_type
        assert data["user_id"] == sample_event.user_id
    
    def test_create_duplicate_event(self, client, sample_event):
        """Test creating a duplicate event (should fail)."""
        # First request should succeed
        response = client.post("/api/v1/events", json=sample_event.dict())
        assert response.status_code == 201
        
        # Second request should fail
        response = client.post("/api/v1/events", json=sample_event.dict())
        assert response.status_code == 409
    
    def test_create_event_missing_required_fields(self, client):
        """Test creating event with missing required fields."""
        incomplete_event = {
            "event_id": "test-event-002",
            # Missing event_type, user_id, timestamp, data
        }
        response = client.post("/api/v1/events", json=incomplete_event)
        assert response.status_code == 422
    
    def test_get_event(self, client, sample_event):
        """Test getting a specific event."""
        # Create event first
        create_response = client.post("/api/v1/events", json=sample_event.dict())
        assert create_response.status_code == 201
        
        # Get event
        event_id = sample_event.event_id
        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == event_id
        assert data["event_type"] == sample_event.event_type
    
    def test_get_nonexistent_event(self, client):
        """Test getting a non-existent event."""
        response = client.get("/api/v1/events/nonexistent-id")
        assert response.status_code == 404
    
    def test_get_events_with_filters(self, client, sample_event):
        """Test getting events with filters."""
        # Create multiple events
        events = [
            sample_event,
            EventCreate(
                event_id="test-event-002",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"}
            ),
            EventCreate(
                event_id="test-event-003",
                event_type="login",
                user_id="user-002",
                session_id="session-002",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.2"}
            )
        ]
        
        for event in events:
            response = client.post("/api/v1/events", json=event.dict())
            assert response.status_code == 201
        
        # Test filtering by event type
        response = client.get("/api/v1/events?event_type=login")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Two login events
        
        # Test filtering by user ID
        response = client.get("/api/v1/events?user_id=user-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Two events for user-001
    
    def test_get_events_pagination(self, client, sample_event):
        """Test getting events with pagination."""
        # Create multiple events
        for i in range(5):
            event = EventCreate(
                event_id=f"test-event-{i:03d}",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"page": f"/page-{i}"}
            )
            response = client.post("/api/v1/events", json=event.dict())
            assert response.status_code == 201
        
        # Test pagination
        response = client.get("/api/v1/events?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        response = client.get("/api/v1/events?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_event_stats(self, client, sample_event):
        """Test getting event statistics."""
        # Create some events
        events = [
            sample_event,
            EventCreate(
                event_id="test-event-002",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"}
            ),
            EventCreate(
                event_id="test-event-003",
                event_type="login",
                user_id="user-002",
                session_id="session-002",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.2"}
            )
        ]
        
        for event in events:
            response = client.post("/api/v1/events", json=event.dict())
            assert response.status_code == 201
        
        # Get stats
        response = client.get("/api/v1/events/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 3
        assert data["unique_users"] == 2
        assert "login" in data["event_types"]
        assert "page_view" in data["event_types"]
    
    def test_get_event_stats_with_filters(self, client, sample_event):
        """Test getting event statistics with filters."""
        # Create events for different users
        events = [
            sample_event,
            EventCreate(
                event_id="test-event-002",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"}
            ),
            EventCreate(
                event_id="test-event-003",
                event_type="login",
                user_id="user-002",
                session_id="session-002",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.2"}
            )
        ]
        
        for event in events:
            response = client.post("/api/v1/events", json=event.dict())
            assert response.status_code == 201
        
        # Get stats filtered by user
        response = client.get("/api/v1/events/stats?user_id=user-001")
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 2
        assert data["unique_users"] == 1
    
    def test_delete_event(self, client, sample_event):
        """Test deleting an event."""
        # Create event first
        create_response = client.post("/api/v1/events", json=sample_event.dict())
        assert create_response.status_code == 201
        
        # Delete event
        event_id = sample_event.event_id
        response = client.delete(f"/api/v1/events/{event_id}")
        assert response.status_code == 204
        
        # Verify event is deleted
        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_event(self, client):
        """Test deleting a non-existent event."""
        response = client.delete("/api/v1/events/nonexistent-id")
        assert response.status_code == 404
    
    def test_create_events_batch(self, client):
        """Test creating multiple events in batch."""
        events = [
            EventCreate(
                event_id="batch-event-001",
                event_type="login",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.1"}
            ),
            EventCreate(
                event_id="batch-event-002",
                event_type="page_view",
                user_id="user-001",
                session_id="session-001",
                timestamp=datetime.now(),
                data={"page": "/dashboard"}
            ),
            EventCreate(
                event_id="duplicate-event",
                event_type="login",
                user_id="user-002",
                session_id="session-002",
                timestamp=datetime.now(),
                data={"ip_address": "192.168.1.2"}
            )
        ]
        
        # Create one event first to test duplicate
        response = client.post("/api/v1/events", json=events[0].dict())
        assert response.status_code == 201
        
        # Create batch
        batch_data = {"events": [event.dict() for event in events]}
        response = client.post("/api/v1/events/batch", json=batch_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["created_count"] == 2  # One duplicate should fail
        assert len(data["failed_events"]) == 1
        assert len(data["errors"]) == 1
    
    def test_invalid_event_type(self, client):
        """Test creating event with invalid event type."""
        invalid_event = EventCreate(
            event_id="test-event-invalid",
            event_type="invalid_type",
            user_id="user-001",
            timestamp=datetime.now(),
            data={"test": "data"}
        )
        
        response = client.post("/api/v1/events", json=invalid_event.dict())
        assert response.status_code == 422
    
    def test_event_data_too_large(self, client):
        """Test creating event with data that's too large."""
        large_data = {"data": "x" * (1024 * 1024 + 1)}  # 1MB + 1 byte
        
        event = EventCreate(
            event_id="test-event-large",
            event_type="login",
            user_id="user-001",
            timestamp=datetime.now(),
            data=large_data
        )
        
        response = client.post("/api/v1/events", json=event.dict())
        assert response.status_code == 422
    
    def test_events_health_endpoint(self, client):
        """Test events health endpoint."""
        response = client.get("/api/v1/events/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "Events endpoint is healthy"