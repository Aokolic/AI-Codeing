"""SQLAlchemy async engine, session factory and Base model."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    # SQLite needs check_same_thread=False via connect_args
    **({"connect_args": {"check_same_thread": False}} if settings.is_sqlite else {}),
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all tables (used in tests and dev startup)."""
    async with engine.begin() as conn:
        # Import models so metadata is populated
        import app.models  # noqa: F401
        from app.database import Base as _Base
        await conn.run_sync(_Base.metadata.create_all)
