"""Unit tests for application configuration."""

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettings:
    """Tests for the Settings configuration class."""

    def test_settings_loads_with_valid_env(self) -> None:
        """Settings loads with DATABASE_URL and JWT_SECRET set; verify all defaults match spec."""
        s = Settings(
            JWT_SECRET="supersecret",
            DATABASE_URL="postgresql+asyncpg://u:p@localhost/testdb",
        )
        assert s.DATABASE_URL == "postgresql+asyncpg://u:p@localhost/testdb"
        assert s.JWT_SECRET == "supersecret"
        assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
        assert s.JWT_REFRESH_EXPIRE_DAYS == 7
        assert s.CORS_ORIGINS == "http://localhost:3000"
        assert s.WS_INITIAL_HOURS == 1
        assert s.GITHUB_TOKEN is None
        assert s.LOG_LEVEL == "INFO"

    def test_settings_raises_on_missing_jwt_secret(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """ValidationError raised when JWT_SECRET is not set."""
        monkeypatch.delenv("JWT_SECRET", raising=False)
        with pytest.raises(ValidationError):
            Settings()

    def test_cors_origins_list_splits_comma_separated(self) -> None:
        """cors_origins_list returns correct list for comma-separated origins."""
        s = Settings(
            JWT_SECRET="test",
            CORS_ORIGINS="http://localhost:3000, http://localhost:3001",
        )
        assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]

    def test_cors_origins_list_empty_string_returns_empty_list(self) -> None:
        """Empty CORS_ORIGINS yields an empty list, not a list with one empty string."""
        s = Settings(JWT_SECRET="test", CORS_ORIGINS="")
        assert s.cors_origins_list == []

    def test_github_token_defaults_to_none(self) -> None:
        """GITHUB_TOKEN is None when not set."""
        s = Settings(JWT_SECRET="test")
        assert s.GITHUB_TOKEN is None
