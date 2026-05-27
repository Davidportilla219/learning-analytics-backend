"""
Pytest configuration for the Auth Service.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database import SessionLocal, Base
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/auth_service_test_db"

# Test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Test session factory
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def async_session() -> AsyncSession:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(async_session: AsyncSession) -> AsyncClient:
    """Create test HTTP client."""
    def get_test_db():
        return async_session
    
    app.dependency_overrides[SessionLocal] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "is_superuser": False
    }


@pytest.fixture
def test_admin_data():
    """Test admin user data."""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "is_superuser": True
    }


@pytest.fixture
def auth_headers(async_client: AsyncClient, test_user_data):
    """Get authentication headers for test user."""
    # Create user first
    response = async_client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = async_client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(async_client: AsyncClient, test_admin_data):
    """Get authentication headers for admin user."""
    # Create admin user first
    response = async_client.post("/api/v1/auth/register", json=test_admin_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": test_admin_data["username"],
        "password": test_admin_data["password"]
    }
    response = async_client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}