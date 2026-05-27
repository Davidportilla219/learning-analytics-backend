"""
API tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint."""
        response = await async_client.get("/")
        assert response.status_code == 200
        assert "Learning Analytics Platform - Auth Service" in response.json()["message"]
        assert response.json()["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "auth-service"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_aggregate(self, async_client: AsyncClient):
        """Test health aggregation endpoint."""
        response = await async_client.get("/api/v1/health-aggregate")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "services" in data
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_user_registration_success(self, async_client: AsyncClient, test_user_data):
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["is_superuser"] == test_user_data["is_superuser"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_user_registration_duplicate_username(self, async_client: AsyncClient, test_user_data):
        """Test user registration with duplicate username."""
        # Register user first time
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register same username again
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_registration_duplicate_email(self, async_client: AsyncClient, test_user_data):
        """Test user registration with duplicate email."""
        # Register user first time
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register same email with different username
        duplicate_email_data = test_user_data.copy()
        duplicate_email_data["username"] = "different_user"
        
        response = await async_client.post("/api/v1/auth/register", json=duplicate_email_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_registration_invalid_data(self, async_client: AsyncClient):
        """Test user registration with invalid data."""
        # Missing required fields
        invalid_data = {"username": "test"}  # Missing email, password
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_user_login_success(self, async_client: AsyncClient, test_user_data):
        """Test successful user login."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_user_login_invalid_credentials(self, async_client: AsyncClient, test_user_data):
        """Test user login with invalid credentials."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, test_user_data, auth_headers):
        """Test getting current user information."""
        response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["is_superuser"] == test_user_data["is_superuser"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, async_client: AsyncClient):
        """Test getting current user without authentication."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_users_admin_only(self, async_client: AsyncClient, test_user_data, admin_headers, auth_headers):
        """Test getting users list (admin only)."""
        # Regular user should not be able to get users list
        response = await async_client.get("/api/v1/auth/users", headers=auth_headers)
        assert response.status_code == 403
        
        # Admin should be able to get users list
        response = await async_client.get("/api/v1/auth/users", headers=admin_headers)
        assert response.status_code == 200
        
        # Should include at least the admin user
        users = response.json()
        assert len(users) >= 1
        assert any(user["username"] == "admin" for user in users)
    
    @pytest.mark.asyncio
    async def test_logout(self, async_client: AsyncClient, auth_headers):
        """Test logout endpoint."""
        response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"