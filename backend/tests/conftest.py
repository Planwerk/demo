"""Shared test fixtures for the Team Statusboard backend."""

import os
from collections.abc import AsyncGenerator

import httpx
import pytest
from httpx import ASGITransport

TEST_JWT_SECRET = "test-secret"

# JWT_SECRET must be set at module level (not in a fixture)
# because app.config.Settings() is instantiated during import-time collection.
os.environ.setdefault("JWT_SECRET", TEST_JWT_SECRET)


@pytest.fixture
def jwt_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set JWT_SECRET to a valid value for tests that construct Settings."""
    monkeypatch.setenv("JWT_SECRET", TEST_JWT_SECRET)


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient]:
    """Yield an httpx AsyncClient wired to the FastAPI test app."""
    from app.main import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
