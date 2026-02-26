"""Shared test fixtures."""

import os

import httpx
import pytest

# Set required env vars before any app imports.
# Uses setdefault so real env vars (e.g. from CI) take precedence.
os.environ.setdefault("JWT_SECRET", "test-secret-for-unit-tests")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")

from app.main import app


@pytest.fixture
def client() -> httpx.AsyncClient:
    """Async HTTP client wired to the FastAPI test app."""
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")
