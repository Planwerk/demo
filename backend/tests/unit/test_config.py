"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettingsDefaults:
    """Tests for Settings default values."""

    def test_settings_default_values(self) -> None:
        """Create Settings with jwt_secret set, verify all defaults."""
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


class TestSettingsValidation:
    """Tests for Settings validation rules."""

    def test_settings_jwt_secret_required(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verify ValidationError when JWT_SECRET is not provided."""
        monkeypatch.delenv("JWT_SECRET", raising=False)
        with pytest.raises(ValidationError):
            Settings()

    def test_settings_env_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Use monkeypatch to set env vars, verify overrides work."""
        monkeypatch.setenv("JWT_SECRET", "override-secret")
        monkeypatch.setenv("JWT_ACCESS_EXPIRE_MINUTES", "60")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("WS_INITIAL_HOURS", "4")
        monkeypatch.setenv("GITHUB_TOKEN", "gh-token-123")

        settings = Settings()

        assert settings.jwt_secret == "override-secret"
        assert settings.jwt_access_expire_minutes == 60
        assert settings.log_level == "DEBUG"
        assert settings.ws_initial_hours == 4
        assert settings.github_token == "gh-token-123"

    def test_cors_origins_parses_comma_separated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Set CORS_ORIGINS as comma-separated string, verify list output."""
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        monkeypatch.setenv(
            "CORS_ORIGINS", "http://localhost:3000,https://example.com"
        )

        settings = Settings()

        assert settings.cors_origins == [
            "http://localhost:3000",
            "https://example.com",
        ]
