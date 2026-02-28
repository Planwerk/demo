"""Tests for app.database — engine, session, Base, get_db."""

import contextlib

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
