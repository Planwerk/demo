"""Tests for app.database module (structural, no live DB required)."""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import AsyncSessionLocal, Base, async_engine, get_db


def test_base_is_declarative_base() -> None:
    """Base is a subclass of DeclarativeBase."""
    assert issubclass(Base, DeclarativeBase)


def test_get_db_is_async_generator() -> None:
    """get_db is an async generator function."""
    assert inspect.isasyncgenfunction(get_db)


def test_async_engine_uses_asyncpg() -> None:
    """async_engine URL drivername contains 'asyncpg'."""
    assert "asyncpg" in async_engine.url.drivername


def test_async_session_local_is_sessionmaker() -> None:
    """AsyncSessionLocal is an async_sessionmaker instance."""
    assert isinstance(AsyncSessionLocal, async_sessionmaker)


async def test_get_db_closes_session_on_caller_exception() -> None:
    """get_db closes the session even when the caller raises an exception."""
    mock_session = AsyncMock()

    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=False)

    with patch("app.database.AsyncSessionLocal", return_value=mock_cm):
        gen = get_db()
        session = await anext(gen)
        assert session is mock_session

        with pytest.raises(RuntimeError, match="caller error"):
            await gen.athrow(RuntimeError("caller error"))

    mock_cm.__aexit__.assert_called_once()
