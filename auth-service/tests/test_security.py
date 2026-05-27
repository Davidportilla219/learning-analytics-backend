"""
Unit tests for JWT security logic.
"""

import pytest
from datetime import timedelta, datetime
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user_id,
    create_auth_response
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test password hashing generates different hashes."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Same password should generate different hashes (due to salt)
        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_password_verification(self):
        """Test password verification with correct and incorrect passwords."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password(wrong_password, hashed) is False
        
        # Empty password should not verify
        assert verify_password("", hashed) is False
    
    def test_verify_password_with_none(self):
        """Test password verification with None values."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # None password should not verify
        assert verify_password(None, hashed) is False
        
        # None hash should not verify
        assert verify_password(password, None) is False


class TestJWTToken:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should contain payload data
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_create_access_token_with_expiration(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        
        # Check expiration time is set correctly
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        assert abs((exp_time - expected_exp).total_seconds()) < 1
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid tokens."""
        # Invalid token
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token("invalid_token")
        
        # Empty token
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token("")
        
        # None token
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token(None)
    
    def test_get_current_user_id(self):
        """Test extracting user ID from token."""
        username = "testuser"
        token = create_access_token({"sub": username})
        
        extracted_user_id = get_current_user_id(token)
        assert extracted_user_id == username
    
    def test_get_current_user_id_invalid(self):
        """Test extracting user ID from invalid token."""
        with pytest.raises(Exception):  # Should raise HTTPException
            get_current_user_id("invalid_token")


class TestAuthResponse:
    """Test authentication response creation."""
    
    def test_create_auth_response(self):
        """Test authentication response DTO creation."""
        token = "test_token_123"
        response = create_auth_response(token, 1800)
        
        assert response.access_token == token
        assert response.token_type == "bearer"
        assert response.expires_in == 1800