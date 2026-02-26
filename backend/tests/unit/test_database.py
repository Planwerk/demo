"""Tests for the database module."""

import inspect

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import AsyncSessionLocal, Base, async_engine, get_db


def test_should_inherit_declarative_base_when_base_defined() -> None:
    assert issubclass(Base, DeclarativeBase)


def test_should_be_async_generator_when_get_db_called() -> None:
    assert inspect.isasyncgenfunction(get_db)


def test_should_use_asyncpg_driver_when_engine_created() -> None:
    assert "asyncpg" in async_engine.url.drivername


def test_should_be_async_sessionmaker_when_session_local_created() -> None:
    assert isinstance(AsyncSessionLocal, async_sessionmaker)
