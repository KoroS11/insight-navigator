"""
NSA-X Database Configuration
Async SQLAlchemy setup for PostgreSQL
"""
from typing import AsyncGenerator

from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

# Parse database URL to detect dialect reliably
db_url = make_url(settings.database_url)
is_sqlite = db_url.drivername.startswith("sqlite")

# Create async engine with dialect-appropriate options
engine_options = {
    "echo": settings.debug,
}

# PostgreSQL-specific pooling options (not supported by SQLite)
if not is_sqlite:
    engine_options.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    # SQLite needs special handling for async
    engine_options.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })

engine = create_async_engine(settings.database_url, **engine_options)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.
    
    Note: Commits any active transaction on success, including those started
    by raw SQL via session.execute(). Callers may rely on rollback semantics
    for error handling.
    """
    async with async_session_maker() as session:
        try:
            yield session
            # Commit if there's an active transaction (covers ORM changes AND raw SQL)
            if session.in_transaction():
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
