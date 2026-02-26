"""
Database Configuration - Async SQLAlchemy with PostgreSQL + PostGIS
Manages async database engine, session factory, and connection lifecycle.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# For Render PostgreSQL, we need to handle SSL differently
# asyncpg doesn't accept sslmode as a URL parameter
if "render.com" in ASYNC_DATABASE_URL:
    # Remove any sslmode parameter from the URL
    if "?sslmode=" in ASYNC_DATABASE_URL:
        ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.split("?sslmode=")[0]
    elif "&sslmode=" in ASYNC_DATABASE_URL:
        ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.split("&sslmode=")[0]
    
    # SSL will be handled by engine parameters instead

# Global engine and session factory
async_engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None

# Declarative base for models
Base = declarative_base()


async def init_db() -> None:
    """
    Initialize async database engine and session factory.
    Called on application startup.
    """
    global async_engine, async_session_factory, Base
    
    # Import here to avoid circular imports
    from src.models import ModelJSONMixin
    
    # Apply ModelJSONMixin to Base without creating a new mapped class
    if not hasattr(Base, 'toJson'):
        # Add the toJson method directly to Base
        Base.toJson = ModelJSONMixin.toJson
    
    # Configure connection parameters
    connect_args = {}
    
    # For Render PostgreSQL, we need to enable SSL
    if "render.com" in ASYNC_DATABASE_URL:
        connect_args["ssl"] = True
    
    # Create async engine with connection pooling
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,  # Set to True for SQL query logging in development
        pool_size=20,  # Max number of connections in pool
        max_overflow=10,  # Extra connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        connect_args=connect_args  # Add SSL if needed
    )
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Prevent lazy loading errors after commit
    )


async def close_db() -> None:
    """
    Close database engine and all connections.
    Called on application shutdown.
    """
    global async_engine
    
    if async_engine:
        await async_engine.dispose()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_async_session() as session:
            result = await session.execute(query)
    
    Yields:
        AsyncSession: Database session
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI route handlers.
    
    Usage in routes:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session
    """
    async with get_async_session() as session:
        yield session
