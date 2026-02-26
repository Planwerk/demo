"""Shared test fixtures for the Team Statusboard backend."""

import os

# Set required env vars before any app module import triggers Settings()
os.environ.setdefault("JWT_SECRET", "test-secret-for-unit-tests")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/testdb")
