"""Tests for application configuration."""

import pytest
from pydantic import ValidationError


class TestSettings:
    """Tests for the Settings class."""

    def test_should_load_defaults_when_valid_env_provided(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")

        from app.config import Settings

        s = Settings()
        assert s.JWT_SECRET == "test-secret"
        assert s.DATABASE_URL == "postgresql+asyncpg://u:p@localhost/db"
        assert s.JWT_ACCESS_EXPIRE_MINUTES == 30
        assert s.JWT_REFRESH_EXPIRE_DAYS == 7
        assert s.CORS_ORIGINS == "http://localhost:3000"
        assert s.WS_INITIAL_HOURS == 1
        assert s.LOG_LEVEL == "INFO"

    def test_should_raise_validation_error_when_jwt_secret_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")

        from app.config import Settings

        with pytest.raises(ValidationError, match="JWT_SECRET"):
            Settings()

    def test_should_split_origins_when_comma_separated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")

        from app.config import Settings

        s = Settings()
        assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]

    def test_should_strip_whitespace_when_cors_origins_have_spaces(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        monkeypatch.setenv("CORS_ORIGINS", "http://a , http://b")

        from app.config import Settings

        s = Settings()
        assert s.cors_origins_list == ["http://a", "http://b"]

    def test_should_return_single_origin_when_no_comma(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "test-secret")

        from app.config import Settings

        s = Settings()
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_should_default_to_none_when_github_token_not_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        from app.config import Settings

        s = Settings()
        assert s.GITHUB_TOKEN is None
