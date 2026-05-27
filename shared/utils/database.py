"""
Database utilities for the Learning Analytics Platform.
"""

import os
from typing import Optional
from urllib.parse import urlunparse, urlparse

import asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker


def get_database_url(service_name: str) -> str:
    """Get database URL for a specific service."""
    
    # Get environment variables with defaults
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    database = f"{service_name}_db"
    
    # Use asyncpg driver for async operations
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


def create_database_url(service_name: str, test_mode: bool = False) -> str:
    """Create database URL with test mode support."""
    
    if test_mode:
        return get_database_url(service_name).replace('_db', '_test_db')
    
    return get_database_url(service_name)


def parse_database_url(database_url: str) -> dict:
    """Parse database URL into components."""
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'username': parsed.username,
        'password': parsed.password,
        'database': parsed.path[1:],  # Remove leading slash
        'driver': parsed.driver or 'asyncpg'
    }


def create_database_engine(database_url: str, pool_size: int = 10, max_overflow: int = 20) -> AsyncEngine:
    """Create async database engine with connection pooling."""
    
    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        echo=False,  # Set to True for debugging SQL queries
        future=True
    )


def create_session_factory(engine: AsyncEngine) -> sessionmaker:
    """Create async session factory."""
    return sessionmaker(
        bind=engine,
        class_=asyncpg.Session,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )


async def test_database_connection(engine: AsyncEngine) -> bool:
    """Test database connection."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            return result.fetchone() is not None
    except Exception:
        return False


async def create_database_if_not_exists(engine: AsyncEngine, database_name: str) -> bool:
    """Create database if it doesn't exist."""
    try:
        # Connect to postgres database to create our database
        postgres_url = str(engine.url).replace(f'/{database_name}', '/postgres')
        postgres_engine = create_async_engine(postgres_url)
        
        async with postgres_engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'"
            )
            
            if not result.fetchone():
                # Create database
                await conn.execute(f'CREATE DATABASE "{database_name}"')
                await conn.commit()
                return True
            
            return False
            
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        if 'postgres_engine' in locals():
            await postgres_engine.dispose()


class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
    
    async def initialize(self, test_mode: bool = False) -> None:
        """Initialize database connection."""
        database_url = create_database_url(self.service_name, test_mode)
        self.engine = create_database_engine(database_url)
        self.session_factory = create_session_factory(self.engine)
        
        # Create database if it doesn't exist
        if not test_mode:
            database_name = parse_database_url(database_url)['database']
            await create_database_if_not_exists(self.engine, database_name)
    
    async def close(self) -> None:
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
    
    async def get_session(self):
        """Get database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()