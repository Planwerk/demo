"""Tests for app.database module."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import Base, get_db, get_engine, get_session_factory

# -------------------------------------------------------------------
# Base
# -------------------------------------------------------------------


class TestBase:
    """Verify the ORM declarative base class."""

    def test_base_is_declarative_base_subclass(self) -> None:
        assert issubclass(Base, DeclarativeBase)

    def test_base_can_be_instantiated_concept(self) -> None:
        """Base itself is abstract but should be a proper class."""
        assert isinstance(Base, type)


# -------------------------------------------------------------------
# get_engine
# -------------------------------------------------------------------


class TestGetEngine:
    """Verify engine creation."""

    def test_get_engine_returns_async_engine(self) -> None:
        engine = get_engine()
        assert isinstance(engine, AsyncEngine)

    def test_get_engine_is_cached(self) -> None:
        first = get_engine()
        second = get_engine()
        assert first is second

    def test_get_engine_uses_settings_database_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///")
        engine = get_engine()
        assert str(engine.url) == "sqlite+aiosqlite:///"


# -------------------------------------------------------------------
# get_session_factory
# -------------------------------------------------------------------


class TestGetSessionFactory:
    """Verify session factory creation."""

    def test_get_session_factory_returns_async_sessionmaker(self) -> None:
        factory = get_session_factory()
        assert isinstance(factory, async_sessionmaker)

    def test_get_session_factory_is_cached(self) -> None:
        first = get_session_factory()
        second = get_session_factory()
        assert first is second


# -------------------------------------------------------------------
# get_db
# -------------------------------------------------------------------


def _mock_session_factory() -> tuple[MagicMock, AsyncMock, AsyncMock]:
    """Create a mock session factory with context manager support.

    Returns the factory, the mock session, and the context manager.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    mock_factory = MagicMock(spec=async_sessionmaker)
    mock_factory.return_value = ctx
    return mock_factory, mock_session, ctx


async def _exhaust_db_generator(gen: AsyncGenerator[AsyncSession]) -> None:
    """Advance the get_db generator past yield to trigger cleanup."""
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()


class TestGetDb:
    """Verify the FastAPI database dependency."""

    def test_get_db_returns_async_generator(self) -> None:
        gen = get_db()
        assert isinstance(gen, AsyncGenerator)

    async def test_get_db_yields_async_session(self) -> None:
        mock_factory, mock_session, _ = _mock_session_factory()

        with patch("app.database.get_session_factory", return_value=mock_factory):
            gen = get_db()
            session = await gen.__anext__()
            assert session is mock_session
            await _exhaust_db_generator(gen)

    async def test_get_db_closes_session_after_use(self) -> None:
        mock_factory, _, ctx = _mock_session_factory()

        with patch("app.database.get_session_factory", return_value=mock_factory):
            gen = get_db()
            await gen.__anext__()
            await _exhaust_db_generator(gen)

            ctx.__aexit__.assert_called_once()
