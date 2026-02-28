"""Tests for app.database — engine, session, Base, get_db."""

import contextlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


def test_base_is_declarative_base() -> None:
    from app.database import Base

    assert issubclass(Base, DeclarativeBase)


def test_async_engine_exists() -> None:
    from app.database import async_engine

    assert async_engine is not None
    assert str(async_engine.url) != ""


def test_async_session_local_exists() -> None:
    from app.database import AsyncSessionLocal

    assert AsyncSessionLocal is not None


async def test_get_db_yields_session() -> None:
    from app.database import get_db

    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    # Cleanup
    with contextlib.suppress(StopAsyncIteration):
        await gen.__anext__()


async def test_get_db_rolls_back_on_exception() -> None:
    from app.database import get_db

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

    with patch("app.database.AsyncSessionLocal", mock_session_factory):
        gen = get_db()
        _session = await gen.__anext__()
        with pytest.raises(RuntimeError, match="db error"):
            await gen.athrow(RuntimeError("db error"))

    mock_session.rollback.assert_awaited_once()
