"""Shared test fixtures for the Team Statusboard backend."""

import os

# Set required environment variables before any app imports.
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
