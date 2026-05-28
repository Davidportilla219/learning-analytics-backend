"""
Database models for the Auth Service.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from shared.contracts.dtos import UserCreateDTO, UserResponseDTO

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    institution = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_superuser": self.is_superuser,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def to_response_dto(self) -> UserResponseDTO:
        """Convert user to response DTO."""
        return UserResponseDTO(
            id=self.id,
            username=self.username,
            name=self.name or self.username,
            email=self.email,
            role="admin" if self.is_superuser else (self.role or "student"),
            is_superuser=self.is_superuser,
            institution=self.institution,
            department=self.department,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_create_dto(cls, user_dto: UserCreateDTO) -> "User":
        """Create user from DTO."""
        from app.core.security import get_password_hash
        return cls(
            username=user_dto.username,
            email=user_dto.email,
            hashed_password=get_password_hash(user_dto.password),
            is_superuser=user_dto.is_superuser,
        )