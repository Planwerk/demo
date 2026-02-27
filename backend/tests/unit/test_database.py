"""Tests for database module (REQ-003, REQ-004)."""

import contextlib
import inspect

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import AsyncSessionLocal, Base, async_engine, get_db


def test_should_be_declarative_base_when_inspected() -> None:
    """Base is a DeclarativeBase subclass."""
    assert issubclass(Base, DeclarativeBase)


def test_should_be_async_generator_when_get_db_inspected() -> None:
    """get_db is an async generator function."""
    assert inspect.isasyncgenfunction(get_db)


def test_should_use_asyncpg_driver_when_engine_created() -> None:
    """async_engine uses the postgresql+asyncpg driver."""
    assert "asyncpg" in async_engine.url.drivername


def test_should_be_async_engine_type_when_engine_created() -> None:
    """async_engine is an AsyncEngine instance."""
    assert isinstance(async_engine, AsyncEngine)


def test_should_be_async_sessionmaker_when_session_local_inspected() -> None:
    """AsyncSessionLocal is an async_sessionmaker instance."""
    assert isinstance(AsyncSessionLocal, async_sessionmaker)


async def test_should_yield_async_session_when_get_db_iterated() -> None:
    """get_db yields an AsyncSession and completes cleanup without error."""
    gen = get_db()
    session = await anext(gen)
    assert isinstance(session, AsyncSession)
    # Exhaust the generator to trigger cleanup
    with contextlib.suppress(StopAsyncIteration):
        await anext(gen)
