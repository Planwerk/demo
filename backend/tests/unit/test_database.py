"""Structural tests for the async database module (no live DB needed)."""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import AsyncSessionLocal, Base, async_engine, get_db


def test_base_is_declarative_base() -> None:
    """Base must be a subclass of SQLAlchemy's DeclarativeBase."""
    assert issubclass(Base, DeclarativeBase)


def test_get_db_is_async_generator() -> None:
    """get_db must be an async generator function."""
    assert inspect.isasyncgenfunction(get_db)


def test_async_engine_uses_asyncpg() -> None:
    """The async engine's URL drivername must contain 'asyncpg'."""
    assert "asyncpg" in async_engine.url.drivername


def test_async_session_local_is_sessionmaker() -> None:
    """AsyncSessionLocal must be an async_sessionmaker instance."""
    assert isinstance(AsyncSessionLocal, async_sessionmaker)


@pytest.mark.asyncio
async def test_get_db_yields_async_session() -> None:
    """get_db must yield an AsyncSession instance and close it cleanly."""
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception() -> None:
    """get_db must call session.rollback() and re-raise when an exception occurs."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session)

    with patch("app.database.AsyncSessionLocal", mock_factory):
        gen = get_db()
        await gen.__anext__()
        with pytest.raises(RuntimeError, match="test error"):
            await gen.athrow(RuntimeError("test error"))

    mock_session.rollback.assert_awaited_once()
