"""Shared test fixtures."""

import os

# Set required env vars before any app imports
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///")
