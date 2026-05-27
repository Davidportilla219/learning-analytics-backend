"""
Unit tests for User model.
"""

import pytest
from app.models.user import User
from shared.contracts.dtos import UserCreateDTO


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_from_create_dto(self):
        """Test creating User from UserCreateDTO."""
        user_dto = UserCreateDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_superuser=False
        )
        
        user = User.from_create_dto(user_dto)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_superuser is False
        assert user.is_active is True
        assert user.hashed_password is not None
        assert user.hashed_password != "testpassword123"  # Should be hashed
    
    def test_user_to_dict(self):
        """Test converting User to dictionary."""
        user_dto = UserCreateDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_superuser=False
        )
        
        user = User.from_create_dto(user_dto)
        user_dict = user.to_dict()
        
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["is_superuser"] is False
        assert user_dict["is_active"] is True
        assert "id" in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
    
    def test_user_to_response_dto(self):
        """Test converting User to UserResponseDTO."""
        user_dto = UserCreateDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_superuser=False
        )
        
        user = User.from_create_dto(user_dto)
        response_dto = user.to_response_dto()
        
        assert response_dto.username == "testuser"
        assert response_dto.email == "test@example.com"
        assert response_dto.is_superuser is False
        assert response_dto.id is not None
        assert response_dto.created_at is not None