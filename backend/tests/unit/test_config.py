"""Tests for app.config — Settings validation and defaults."""

import pytest
from pydantic import ValidationError


def test_settings_loads_with_required_env_vars() -> None:
    from app.config import Settings

    s = Settings(jwt_secret="s3cret", database_url="postgresql+asyncpg://localhost/db")
    assert s.jwt_secret == "s3cret"
    assert s.database_url == "postgresql+asyncpg://localhost/db"


def test_settings_defaults() -> None:
    from app.config import Settings

    s = Settings(jwt_secret="s3cret")
    assert s.cors_origins == "http://localhost:3000"
    assert s.jwt_access_expire_minutes == 30
    assert s.jwt_refresh_expire_days == 7
    assert s.ws_initial_hours == 1
    assert s.github_token is None
    assert s.log_level == "INFO"


def test_settings_missing_jwt_secret_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    from app.config import Settings

    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(_env_file=None)


def test_settings_reads_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "from-env")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    from app.config import Settings

    s = Settings(_env_file=None)
    assert s.jwt_secret == "from-env"
    assert s.log_level == "DEBUG"


def test_cors_origins_list_splits_comma_separated() -> None:
    from app.config import Settings

    s = Settings(jwt_secret="s3cret", cors_origins="http://a.com, http://b.com , http://c.com")
    assert s.cors_origins_list == ["http://a.com", "http://b.com", "http://c.com"]


def test_cors_origins_list_single_origin() -> None:
    from app.config import Settings

    s = Settings(jwt_secret="s3cret", cors_origins="http://localhost:3000")
    assert s.cors_origins_list == ["http://localhost:3000"]


def test_module_level_settings_instance() -> None:
    from app.config import settings

    assert settings.jwt_secret  # noqa: S105 — test value
    assert isinstance(settings.jwt_secret, str)
