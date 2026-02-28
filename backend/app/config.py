"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings validated at startup via pydantic-settings."""

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
        """Split comma-separated CORS_ORIGINS into a list."""
        return [
            origin
            for raw in self.CORS_ORIGINS.split(",")
            if (origin := raw.strip())
        ]


settings = Settings()
