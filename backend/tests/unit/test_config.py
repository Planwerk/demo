"""Tests for app.config Settings class."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_loads_with_valid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings object created with DATABASE_URL and JWT_SECRET; defaults match spec."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "secret")
    s = Settings()
    assert s.DATABASE_URL == "postgresql+asyncpg://u:p@localhost/db"
    assert s.JWT_SECRET == "secret"
    assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
    assert s.JWT_REFRESH_EXPIRE_DAYS == 7
    assert s.CORS_ORIGINS == "http://localhost:3000"
    assert s.WS_INITIAL_HOURS == 1
    assert s.LOG_LEVEL == "INFO"


def test_settings_raises_on_missing_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """ValidationError raised when JWT_SECRET is not set."""
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings()


def test_cors_origins_list_splits_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list splits comma-separated string into a list."""
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_list_single_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list returns a single-element list when no comma present."""
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000"]


def test_cors_origins_list_strips_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list strips whitespace around comma-separated origins."""
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("CORS_ORIGINS", " http://a.com , http://b.com ")
    s = Settings()
    assert s.cors_origins_list == ["http://a.com", "http://b.com"]


def test_cors_origins_list_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list returns a single empty string when CORS_ORIGINS is empty."""
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.setenv("CORS_ORIGINS", "")
    s = Settings()
    assert s.cors_origins_list == [""]


def test_github_token_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """GITHUB_TOKEN is None when not set in environment."""
    monkeypatch.setenv("JWT_SECRET", "secret")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    s = Settings()
    assert s.GITHUB_TOKEN is None
