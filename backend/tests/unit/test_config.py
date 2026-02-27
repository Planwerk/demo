"""Tests for application configuration (REQ-002)."""

import pytest
from pydantic import ValidationError


def test_settings_loads_with_valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings loads successfully with required env vars; defaults are correct."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from app.config import Settings

    s = Settings()
    assert s.JWT_SECRET == "test-secret"
    assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
    assert s.JWT_REFRESH_EXPIRE_DAYS == 7
    assert s.CORS_ORIGINS == "http://localhost:3000"
    assert s.WS_INITIAL_HOURS == 1
    assert s.LOG_LEVEL == "INFO"


def test_settings_raises_on_missing_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """ValidationError raised when JWT_SECRET is not set."""
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")

    from app.config import Settings

    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings()


def test_cors_origins_list_splits_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list splits comma-separated CORS_ORIGINS correctly."""
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")

    from app.config import Settings

    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_list_single_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """cors_origins_list returns single-element list for single origin."""
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    from app.config import Settings

    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000"]


def test_github_token_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """GITHUB_TOKEN is None when not set."""
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    from app.config import Settings

    s = Settings()
    assert s.GITHUB_TOKEN is None
