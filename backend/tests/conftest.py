"""Shared test fixtures for the Team Statusboard backend."""

import os

import pytest

# Set required environment variables before any app imports.
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")


@pytest.fixture()
def settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set JWT_SECRET and DATABASE_URL env vars for Settings instantiation."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
