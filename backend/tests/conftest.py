"""Shared test fixtures for the backend test suite.

Note: No database_url override is configured here because no tests currently
require a real database connection. When the first ORM model is added, a
``database_url`` fixture pointing to ``sqlite+aiosqlite://`` should be
introduced for integration tests.
"""

from collections.abc import AsyncGenerator

import httpx
import pytest
from httpx import ASGITransport

from app.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Return Settings configured for testing."""
    return Settings(jwt_secret="test-secret-key")


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    """Provide an async HTTP client wired to the FastAPI app.

    Note: tests/unit/test_main.py overrides this fixture with its own
    version that controls environment variables for CORS testing.
    """
    from app.main import app

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac
