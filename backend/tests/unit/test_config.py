"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.fixture
def _base_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/test")
    monkeypatch.setenv("JWT_SECRET", "test-secret")


@pytest.mark.usefixtures("_base_env")
class TestSettingsDefaults:
    def test_loads_with_valid_env(self) -> None:
        s = Settings()
        assert s.DATABASE_URL == "postgresql+asyncpg://u:p@localhost/test"
        assert s.JWT_SECRET == "test-secret"

    def test_jwt_access_expire_default(self) -> None:
        assert Settings().JWT_ACCESS_EXPIRE_MINUTES == 30

    def test_jwt_refresh_expire_default(self) -> None:
        assert Settings().JWT_REFRESH_EXPIRE_DAYS == 7

    def test_cors_origins_default(self) -> None:
        assert Settings().CORS_ORIGINS == "http://localhost:3000"

    def test_ws_initial_hours_default(self) -> None:
        assert Settings().WS_INITIAL_HOURS == 1

    def test_log_level_default(self) -> None:
        assert Settings().LOG_LEVEL == "INFO"

    def test_github_token_defaults_to_none(self) -> None:
        assert Settings().GITHUB_TOKEN is None


def test_settings_raises_on_missing_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/test")
    with pytest.raises(ValidationError):
        Settings()


def test_cors_origins_list_splits_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_list_strips_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000 , http://localhost:3001")
    s = Settings()
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("CORS_ORIGINS", "")
    s = Settings()
    assert s.cors_origins_list == [""]


def test_jwt_access_expire_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("JWT_ACCESS_EXPIRE_MINUTES", "0")
    s = Settings()
    assert s.JWT_ACCESS_EXPIRE_MINUTES == 0


def test_ws_initial_hours_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("WS_INITIAL_HOURS", "0")
    s = Settings()
    assert s.WS_INITIAL_HOURS == 0
