"""Application configuration (pydantic-settings, env-driven). CLAUDE.md §47."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # CORS - comma-separated origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Demo mode: skip live scheduler/sync, just ensure demo fixtures are loaded
    demo_mode: bool = False

    # IRD integration
    ird_api_base_url: str = "https://prize.ird.gov.np/api/v1/public"
    ird_page_limit: int = 100
    ird_request_timeout_seconds: float = 15.0
    ird_max_retries: int = 3

    # Scheduler
    scheduler_enabled: bool = True
    scheduler_timezone: str = "Asia/Kathmandu"

    # Logging
    log_level: str = "INFO"

    # Auth (JWT). The default secret is clearly marked insecure and is only
    # here so the app runs out of the box for local/demo use without any
    # config; app.main logs a loud warning at startup if it's still in use.
    # Set a real random value via JWT_SECRET before any shared/public deployment.
    jwt_secret: str = "insecure-dev-secret-change-me-before-any-real-deployment"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
