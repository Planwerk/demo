"""Tests for database module structure and exports."""

import inspect


def test_should_be_declarative_base_when_base_imported() -> None:
    from sqlalchemy.orm import DeclarativeBase

    from app.database import Base

    assert issubclass(Base, DeclarativeBase)


def test_should_be_async_generator_when_get_db_called() -> None:
    from app.database import get_db

    assert inspect.isasyncgenfunction(get_db)


def test_should_use_asyncpg_driver_when_engine_created() -> None:
    from app.database import async_engine

    assert "asyncpg" in str(async_engine.url.drivername)


def test_should_be_async_sessionmaker_when_session_local_imported() -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.database import AsyncSessionLocal

    assert isinstance(AsyncSessionLocal, async_sessionmaker)
