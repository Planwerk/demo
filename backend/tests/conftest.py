"""Shared test fixtures for the backend test suite."""

import os

# Ensure JWT_SECRET is set before any app module imports
os.environ.setdefault("JWT_SECRET", "test-secret-key")

from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings, get_settings
from app.database import get_engine


@pytest.fixture(autouse=True)
def _clear_caches() -> Generator[None]:
    """Clear lru_cache singletons between tests for isolation."""
    get_settings.cache_clear()
    get_engine.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()


@pytest.fixture
def test_settings() -> Settings:
    """Provide a Settings instance suitable for unit testing."""
    return Settings(
        jwt_secret="test-secret-key",
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Provide an async HTTP client wired to the FastAPI test app."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
