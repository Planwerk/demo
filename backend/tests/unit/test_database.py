"""Tests for database module structure (no live DB required)."""

import inspect

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import AsyncSessionLocal, Base, async_engine, get_db


def test_base_is_declarative_base() -> None:
    assert issubclass(Base, DeclarativeBase)


def test_get_db_is_async_generator() -> None:
    assert inspect.isasyncgenfunction(get_db)


def test_async_engine_uses_asyncpg() -> None:
    assert "asyncpg" in str(async_engine.url.drivername)


def test_async_engine_is_async_engine() -> None:
    from sqlalchemy.ext.asyncio import AsyncEngine

    assert isinstance(async_engine, AsyncEngine)


def test_session_local_is_async_sessionmaker() -> None:
    assert isinstance(AsyncSessionLocal, async_sessionmaker)
