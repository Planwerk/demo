"""Shared test fixtures and environment setup."""

import os

# Set required env vars BEFORE any app imports to satisfy module-level Settings().
os.environ.setdefault("JWT_SECRET", "test-secret-for-unit-tests")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
