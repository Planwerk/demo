"""Tests for application configuration (REQ-002)."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_should_load_settings_when_valid_env_vars_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings loads successfully when required env vars are set."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    s = Settings()
    assert s.JWT_SECRET == "test-secret"  # noqa: S105
    assert s.DATABASE_URL == "postgresql+asyncpg://u:p@localhost/db"


def test_should_use_defaults_when_optional_vars_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    """All optional settings use documented defaults."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    s = Settings()
    assert s.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/statusboard"
    assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
    assert s.JWT_REFRESH_EXPIRE_DAYS == 7
    assert s.CORS_ORIGINS == "http://localhost:3000"
    assert s.WS_INITIAL_HOURS == 1
    assert s.LOG_LEVEL == "INFO"


def test_should_raise_validation_error_when_jwt_secret_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ValidationError raised when JWT_SECRET is missing."""
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_should_split_origins_when_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list splits comma-separated CORS_ORIGINS."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_should_return_single_element_list_when_one_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """cors_origins_list returns a single-element list for a single origin."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000"]


def test_should_filter_empty_origins_when_trailing_comma(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list ignores empty entries from trailing commas."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000"]


def test_should_return_empty_list_when_cors_origins_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """cors_origins_list returns empty list when CORS_ORIGINS is empty string."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("CORS_ORIGINS", "")
    s = Settings()
    assert s.cors_origins_list == []


def test_should_default_to_none_when_github_token_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """GITHUB_TOKEN is None when not set."""
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    s = Settings()
    assert s.GITHUB_TOKEN is None
