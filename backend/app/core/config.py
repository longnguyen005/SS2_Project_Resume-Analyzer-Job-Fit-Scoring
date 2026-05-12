from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_CONFIG_FILE = Path(__file__).resolve()
_BACKEND_ROOT = _CONFIG_FILE.parents[2]
_PROJECT_ROOT = _CONFIG_FILE.parents[3]
_ENV_FILE_CANDIDATES = (
    _BACKEND_ROOT / ".env",
    _PROJECT_ROOT / ".env",
)
_ENV_FILES = tuple(str(path) for path in _ENV_FILE_CANDIDATES if path.exists())


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
    r2_enabled: bool = False
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "resume-analyzer-files"
    r2_bucket_region: str = "auto"
    r2_public_base_url: str = ""
    r2_key_prefix: str = "uploads"
    n8n_webhook_url: str = ""
    n8n_basic_auth_user: str = ""
    n8n_basic_auth_password: str = ""
    n8n_internal_shared_secret: str = ""
    n8n_webhook_timeout_seconds: int = 60
    n8n_webhook_max_attempts: int = 2
    n8n_processing_claim_ttl_seconds: int = 900
    ocr_fallback_enabled: bool = True
    ocr_languages: str = "eng+vie"
    ocr_language_fallback: str = "eng"
    ocr_render_scale: float = 2.0
    cors_origins: str = "http://localhost:5173"
    ai_provider_label: str = "gemini"
    ai_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    ai_api_key: str = ""
    ai_model: str = "gemini-2.5-flash"
    ai_fallback_provider_label: str = "gemini-fallback"
    ai_fallback_base_url: str = ""
    ai_fallback_api_key: str = ""
    ai_fallback_model: str = "gemini-2.5-flash-lite"
    ai_request_timeout_seconds: int = 45
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES or None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def r2_is_configured(self) -> bool:
        return bool(
            self.r2_enabled
            and self.r2_endpoint_url.strip()
            and self.r2_access_key_id.strip()
            and self.r2_secret_access_key.strip()
            and self.r2_bucket_name.strip()
        )

    @property
    def n8n_is_configured(self) -> bool:
        return bool(
            self.n8n_webhook_url.strip()
            and self.n8n_internal_shared_secret.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
