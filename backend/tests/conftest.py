"""Shared test configuration and fixtures."""

import os

# Set required env vars before any app module is imported during collection.
os.environ.setdefault("JWT_SECRET", "test-secret-for-testing")
