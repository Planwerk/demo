"""Tests for database module (REQ-003, REQ-004)."""

import inspect

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


def test_base_is_declarative_base() -> None:
    """Base inherits from DeclarativeBase."""
    from app.database import Base

    assert issubclass(Base, DeclarativeBase)


def test_get_db_is_async_generator() -> None:
    """get_db is an async generator function."""
    from app.database import get_db

    assert inspect.isasyncgenfunction(get_db)


async def test_get_db_yields_async_session() -> None:
    """get_db yields an AsyncSession instance."""
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.database import get_db

    agen = get_db()
    session = await anext(agen)
    assert isinstance(session, AsyncSession)
    await agen.aclose()


def test_async_engine_uses_asyncpg() -> None:
    """async_engine URL uses postgresql+asyncpg driver."""
    from app.database import async_engine

    assert async_engine.url.drivername == "postgresql+asyncpg"


def test_async_session_local_is_sessionmaker() -> None:
    """AsyncSessionLocal is an async_sessionmaker instance."""
    from app.database import AsyncSessionLocal

    assert isinstance(AsyncSessionLocal, async_sessionmaker)
