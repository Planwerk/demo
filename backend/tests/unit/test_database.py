"""Unit tests for app.database module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.database import Base, get_db


class TestBase:
    """Tests for the ORM declarative base."""

    def test_base_is_declarative_base(self) -> None:
        """Base must inherit from DeclarativeBase."""
        assert issubclass(Base, DeclarativeBase)


class TestGetDb:
    """Tests for the get_db async generator dependency."""

    @pytest.mark.asyncio
    async def test_get_db_yields_async_session(self) -> None:
        """get_db() should yield an AsyncSession instance."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_factory = MagicMock()
        # The factory is called with no args to create a session context manager.
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_cm

        with patch("app.database.get_session_factory", return_value=mock_factory):
            gen = get_db()
            session = await gen.__anext__()
            assert isinstance(session, AsyncSession)
            # Clean up the generator
            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()

    @pytest.mark.asyncio
    async def test_get_db_closes_session_after_use(self) -> None:
        """Session context manager __aexit__ must be called after generator exits."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_factory = MagicMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_cm

        with patch("app.database.get_session_factory", return_value=mock_factory):
            gen = get_db()
            _ = await gen.__anext__()
            # Exhaust the generator to trigger cleanup
            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()

        # __aexit__ should have been called once (session closed)
        mock_cm.__aexit__.assert_awaited_once()
