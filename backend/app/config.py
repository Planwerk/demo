"""Application configuration via environment variables.

Uses pydantic-settings to load and validate configuration from environment
variables and an optional .env file. Missing required fields (such as
JWT_SECRET) raise a validation error at import time.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/statusboard"
    JWT_SECRET: str
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"
    WS_INITIAL_HOURS: int = 1
    GITHUB_TOKEN: str | None = None
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        """Split CORS_ORIGINS by comma, strip whitespace, and filter out empty entries."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
