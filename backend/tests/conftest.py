"""Shared test fixtures."""

import os

# Set required env vars BEFORE any app imports because app.config.Settings()
# is instantiated at module level — importing any app module triggers validation
# and will fail without these variables.
os.environ.setdefault("JWT_SECRET", "test-secret-for-testing")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
