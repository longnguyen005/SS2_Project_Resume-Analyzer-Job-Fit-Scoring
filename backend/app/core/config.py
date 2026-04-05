from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resume Analyzer API"
    api_v1_prefix: str = "/api/v1"
    backend_public_url: str = "http://localhost:8000"
    frontend_public_url: str = "http://localhost:5173"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/resume_analyzer"
    database_url_sync: str = "postgresql+psycopg://postgres:postgres@db:5432/resume_analyzer"
    jwt_secret_key: str = "change-me-in-production"
    session_secret_key: str = "change-me-session-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_dir: str = "uploads"
    max_file_size_mb: int = 10
    cors_origins: str = "http://localhost:5173"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
