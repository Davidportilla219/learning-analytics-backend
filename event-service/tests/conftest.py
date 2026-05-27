"""
Pytest configuration and fixtures for the Event Service.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db_session
from app.main import app
import os

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
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
def sample_event_data():
    """Sample event data for testing."""
    return {
        "event_id": "test-event-001",
        "event_type": "login",
        "user_id": "user-001",
        "session_id": "session-001",
        "course_id": "course-001",
        "timestamp": "2024-01-01T10:00:00",
        "data": {"ip_address": "192.168.1.1", "user_agent": "Mozilla/5.0"},
        "metadata": {"device": "desktop", "browser": "chrome"}
    }