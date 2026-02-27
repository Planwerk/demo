"""Shared test fixtures for the backend test suite."""

import os

# JWT_SECRET must be set before any app imports because app.config declares a
# module-level `settings = Settings()` that validates on import. Without this,
# importing any app module raises a ValidationError.
os.environ.setdefault("JWT_SECRET", "test-secret-for-unit-tests")
