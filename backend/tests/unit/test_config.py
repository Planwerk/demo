"""Unit tests for application configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings


def _make_settings() -> Settings:
    """Create a Settings instance without reading .env files."""
    return Settings(_env_file=None)


@pytest.mark.usefixtures("jwt_env")
class TestSettingsLoadsWithValidEnv:
    """Settings object created successfully with required values provided."""

    def test_settings_loads_with_valid_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@host:5432/db")

        s = _make_settings()

        assert s.DATABASE_URL == "postgresql+asyncpg://u:p@host:5432/db"
        assert s.JWT_SECRET == "test-secret"
        assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
        assert s.JWT_REFRESH_EXPIRE_DAYS == 7
        assert s.CORS_ORIGINS == "http://localhost:3000"
        assert s.WS_INITIAL_HOURS == 1
        assert s.GITHUB_TOKEN is None
        assert s.LOG_LEVEL == "INFO"


class TestSettingsRaisesOnMissingJwtSecret:
    """ValidationError raised when JWT_SECRET is not set or invalid."""

    def test_settings_raises_on_missing_jwt_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("JWT_SECRET", raising=False)

        with pytest.raises(ValidationError):
            _make_settings()

    def test_settings_raises_on_empty_jwt_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JWT_SECRET", "")

        with pytest.raises(ValidationError):
            _make_settings()

    def test_settings_raises_on_whitespace_jwt_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "   ")

        with pytest.raises(ValidationError):
            _make_settings()


@pytest.mark.usefixtures("jwt_env")
class TestCorsOriginsListSplitsCommaSeparated:
    """cors_origins_list returns split list from comma-separated string."""

    def test_cors_origins_list_splits_comma_separated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")

        s = _make_settings()

        assert s.cors_origins_list == [
            "http://localhost:3000",
            "http://localhost:3001",
        ]

    def test_cors_origins_list_strips_whitespace(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Values with spaces are stripped."""
        monkeypatch.setenv(
            "CORS_ORIGINS",
            "http://localhost:3000, http://localhost:3001",
        )

        s = _make_settings()

        assert s.cors_origins_list == [
            "http://localhost:3000",
            "http://localhost:3001",
        ]

    def test_cors_origins_list_ignores_trailing_comma(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Trailing commas produce no empty entries."""
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,")

        s = _make_settings()

        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_cors_origins_list_ignores_leading_and_multiple_commas(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Leading and consecutive commas produce no empty entries."""
        monkeypatch.setenv("CORS_ORIGINS", ",http://localhost:3000,,")

        s = _make_settings()

        assert s.cors_origins_list == ["http://localhost:3000"]


@pytest.mark.usefixtures("jwt_env")
class TestGithubTokenDefaultsToNone:
    """GITHUB_TOKEN is None when not set in environment."""

    def test_github_token_defaults_to_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        s = _make_settings()

        assert s.GITHUB_TOKEN is None


@pytest.mark.usefixtures("jwt_env")
class TestDefaultValuesMatchSpec:
    """Default values match the specification."""

    def test_default_values_match_spec(self) -> None:
        s = _make_settings()

        assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
        assert s.JWT_REFRESH_EXPIRE_DAYS == 7
        assert s.CORS_ORIGINS == "http://localhost:3000"
        assert s.WS_INITIAL_HOURS == 1
        assert s.LOG_LEVEL == "INFO"
