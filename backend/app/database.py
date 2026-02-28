"""Async SQLAlchemy engine, session factory, and declarative base."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Yield an async database session, ensuring cleanup on completion."""
    async with AsyncSessionLocal() as session:
        yield session
