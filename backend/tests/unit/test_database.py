"""Unit tests for async database engine, session factory, and base model."""

import inspect

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database import Base, get_db, get_engine, get_session_factory


class TestBaseIsDeclarativeBase:
    """Base is a subclass of DeclarativeBase."""

    def test_base_is_declarative_base(self) -> None:
        assert issubclass(Base, DeclarativeBase)


class TestGetDbIsAsyncGenerator:
    """get_db is an async generator function."""

    def test_get_db_is_async_generator(self) -> None:
        assert inspect.isasyncgenfunction(get_db)


class TestGetEngineUsesAsyncpg:
    """get_engine() returns an engine with asyncpg driver."""

    def test_get_engine_uses_asyncpg(self) -> None:
        engine = get_engine()
        assert "asyncpg" in engine.url.drivername


class TestGetSessionFactoryIsSessionmaker:
    """get_session_factory() returns an async_sessionmaker instance."""

    def test_get_session_factory_is_sessionmaker(self) -> None:
        assert isinstance(get_session_factory(), async_sessionmaker)
