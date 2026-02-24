"""Async database engine, session factory, and FastAPI dependency."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Create and cache the async SQLAlchemy engine.

    Uses ``@lru_cache`` to create a module-level singleton. Tests that need
    different settings must call ``get_engine.cache_clear()`` (and
    ``get_session_factory.cache_clear()``) before and after the test.
    """
    return create_async_engine(get_settings().database_url)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create and cache the async session factory.

    Singleton via ``@lru_cache`` — see ``get_engine`` for testing notes.
    """
    return async_sessionmaker(get_engine(), expire_on_commit=False)


class Base(DeclarativeBase):
    """ORM declarative base for all models."""


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Yield an async database session (FastAPI dependency).

    The ``async with`` block ensures the session is properly closed
    even when an exception is raised inside the request handler.
    """
    async with get_session_factory()() as session:
        yield session
