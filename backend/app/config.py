"""Application configuration loaded from environment variables."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://USER:PASSWORD@localhost:5432/statusboard"
    JWT_SECRET: str
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000"
    WS_INITIAL_HOURS: int = 1
    GITHUB_TOKEN: str | None = None
    LOG_LEVEL: str = "INFO"

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_must_not_be_blank(cls, v: str) -> str:
        """Reject empty or whitespace-only JWT_SECRET values."""
        if not v.strip():
            msg = "JWT_SECRET must not be empty or whitespace-only"
            raise ValueError(msg)
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Split comma-separated CORS_ORIGINS into a list, filtering out empty values."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
