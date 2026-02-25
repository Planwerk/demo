"""Tests for app.config module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettingsDefaults:
    """Verify default values when only required fields are set."""

    def test_settings_default_values(self) -> None:
        settings = Settings(jwt_secret="test-secret")

        assert settings.database_url == (
            "postgresql+asyncpg://user:pass@localhost:5432/statusboard"
        )
        assert settings.jwt_secret == "test-secret"
        assert settings.jwt_access_expire_minutes == 30
        assert settings.jwt_refresh_expire_days == 7
        assert settings.cors_origins == ["http://localhost:3000"]
        assert settings.ws_initial_hours == 1
        assert settings.github_token is None
        assert settings.log_level == "INFO"

    def test_settings_jwt_secret_required(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("JWT_SECRET", raising=False)
        with pytest.raises(ValidationError):
            Settings()


class TestSettingsOverride:
    """Verify environment variable overrides."""

    def test_settings_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://other:pw@db:5432/x")
        monkeypatch.setenv("JWT_SECRET", "env-secret")
        monkeypatch.setenv("JWT_ACCESS_EXPIRE_MINUTES", "60")
        monkeypatch.setenv("JWT_REFRESH_EXPIRE_DAYS", "14")
        monkeypatch.setenv("CORS_ORIGINS", "http://a.com")
        monkeypatch.setenv("WS_INITIAL_HOURS", "4")
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_abc")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()

        assert settings.database_url == "postgresql+asyncpg://other:pw@db:5432/x"
        assert settings.jwt_secret == "env-secret"
        assert settings.jwt_access_expire_minutes == 60
        assert settings.jwt_refresh_expire_days == 14
        assert settings.cors_origins == ["http://a.com"]
        assert settings.ws_initial_hours == 4
        assert settings.github_token == "ghp_abc"
        assert settings.log_level == "DEBUG"

    def test_cors_origins_parses_comma_separated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "s")
        monkeypatch.setenv("CORS_ORIGINS", "a,b")

        settings = Settings()

        assert settings.cors_origins == ["a", "b"]

    def test_cors_origins_parses_json_array(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "s")
        monkeypatch.setenv("CORS_ORIGINS", '["http://a.com","http://b.com"]')

        settings = Settings()

        assert settings.cors_origins == ["http://a.com", "http://b.com"]
