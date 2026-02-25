"""Application configuration loaded from environment variables."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import TYPE_CHECKING

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources.providers.env import EnvSettingsSource

if TYPE_CHECKING:
    from pydantic_settings import PydanticBaseSettingsSource


class _CorsAwareEnvSource(EnvSettingsSource):
    """Env source that gracefully handles comma-separated CORS_ORIGINS."""

    def decode_complex_value(
        self, field_name: str, field: object, value: object
    ) -> object:
        if field_name == "cors_origins" and isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # Fall through so the field_validator can split on commas
                return value
        return super().decode_complex_value(field_name, field, value)  # type: ignore[arg-type]  # pydantic-settings base class has imprecise field types


class Settings(BaseSettings):
    """Application settings populated from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = (
        "postgresql+asyncpg://user:pass@localhost:5432/statusboard"
    )
    jwt_secret: str
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    cors_origins: list[str] = ["http://localhost:3000"]
    ws_initial_hours: int = 1
    github_token: str | None = None
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        """Accept a comma-separated string and split into a list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Use a custom env source that handles comma-separated lists."""
        return (
            init_settings,
            _CorsAwareEnvSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
