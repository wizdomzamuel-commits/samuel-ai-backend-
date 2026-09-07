"""
Application configuration.

Settings are loaded from environment variables (or a local .env file
during development). See .env.example for the full list of variables.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "Samuel AI"
    ENVIRONMENT: str = "development"  # development | production
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    # Simple shared-secret API key for a personal assistant.
    # Sent by clients as the "X-API-Key" header.
    API_KEY: str = "change-me"

    # --- Database ---
    # Defaults to a local SQLite file. On Railway, set DATABASE_URL to the
    # provided Postgres connection string (Railway injects this automatically
    # if you attach a Postgres plugin).
    DATABASE_URL: str = "sqlite:///./samuel_ai.db"

    # --- OpenAI ---
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # --- Scheduler ---
    ENABLE_SCHEDULER: bool = True
    DAILY_SUMMARY_HOUR: int = 20   # 8 PM local server time
    DAILY_SUMMARY_MINUTE: int = 0
    WEEKLY_SUMMARY_DAY_OF_WEEK: str = "sun"  # apscheduler cron day_of_week
    WEEKLY_SUMMARY_HOUR: int = 21
    TIMEZONE: str = "UTC"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> "Settings":
    """Cached settings accessor so we don't re-parse env vars on every call."""
    return Settings()
