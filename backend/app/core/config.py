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

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
