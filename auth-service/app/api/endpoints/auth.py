"""
Authentication API endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    create_auth_response,
    get_current_user_id
)
from app.models.user import User
from app.database import get_db
from shared.contracts.dtos import (
    AuthRequestDTO,
    AuthResponseDTO,
    UserCreateDTO,
    UserResponseDTO
)

router = APIRouter()


@router.post("/login", response_model=AuthResponseDTO)
async def login(
    request: AuthRequestDTO,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint."""
    
    # Get user from database
    query = select(User).where(User.username == request.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return create_auth_response(access_token, settings.JWT_EXPIRE_MINUTES * 60)


@router.post("/register", response_model=UserResponseDTO)
async def register(
    request: UserCreateDTO,
    db: AsyncSession = Depends(get_db)
):
    """User registration endpoint."""
    
    # Check if user already exists
    query = select(User).where(
        (User.username == request.username) | (User.email == request.email)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.username == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    user = User.from_create_dto(request)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user.to_response_dto()


@router.post("/logout")
async def logout():
    """User logout endpoint."""
    # In a real application, you might want to add the token to a blacklist
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponseDTO)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_current_user_id)
):
    """Get current user information."""
    
    # Get user from database
    query = select(User).where(User.username == token)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user.to_response_dto()


@router.get("/users", response_model=list[UserResponseDTO])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_current_user_id)
):
    """Get all users (admin only)."""
    
    # Check if current user is superuser
    query = select(User).where(User.username == token)
    result = await db.execute(query)
    current_user = result.scalar_one_or_none()
    
    if not current_user or not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get all users
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [user.to_response_dto() for user in users]