"""Application configuration via environment variables and .env file."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = (
        "postgresql+asyncpg://user:pass@localhost:5432/statusboard"
    )
    jwt_secret: str
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    cors_origins: str | list[str] = ["http://localhost:3000"]
    ws_initial_hours: int = 1
    github_token: str | None = None
    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Split comma-separated string into a list."""
        if isinstance(v, str):
            return [s.strip() for s in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
