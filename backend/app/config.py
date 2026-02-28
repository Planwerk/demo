"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and .env file support."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(default="postgresql+asyncpg://localhost:5432/statusboard")
    jwt_secret: str
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    cors_origins: str = "http://localhost:3000"
    ws_initial_hours: int = 1
    github_token: str | None = None
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        """Split CORS_ORIGINS by comma and strip whitespace."""
        return [o for o in (s.strip() for s in self.cors_origins.split(",")) if o]


settings = Settings()
