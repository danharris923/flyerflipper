"""
Database configuration and session management for FlyerFlutter application.
Uses SQLAlchemy 2.0 with SQLite database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings


# SQLAlchemy 2.0 Declarative Base
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Database Engine Configuration
# For SQLite, we use both sync and async engines
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Async engine for async operations (when needed)
if "sqlite" in settings.DATABASE_URL:
    async_database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = settings.DATABASE_URL

async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG
)

# Session Factories
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Async dependency function to get database session.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db():
    """Initialize the database by creating tables."""
    create_tables()