"""
api/config.py
=============
Centralized application configuration.

All environment variables are read ONCE from the .env file here.
Every other file imports from this module — never from os.getenv() directly.

Why pydantic-settings?
  • Automatic type casting   (e.g. DB_PORT="5432" → int 5432)
  • Validation on startup    (missing required vars crash immediately, not mid-request)
  • IDE autocomplete         (you see every config field in one place)
  • Production best practice (used at Netflix, Meta, Google internally)
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    Field names MUST match your .env variable names exactly (case-insensitive).
    """

    # ── Database ──────────────────────────────────────────────────────────────
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "TIGER"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432          # pydantic auto-casts str → int
    DB_NAME: str = "job_market_db"

    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = "development"   # development | staging | production
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    APP_TITLE: str = "Job Market Intelligence API"
    APP_DESCRIPTION: str = (
        "AI-Powered Global Job Market Intelligence & Workforce Analytics Platform"
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated origins allowed to call this API.
    # In production this becomes "https://yourdomain.com"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ── SQLAlchemy Connection Pool ────────────────────────────────────────────
    # pool_size    = persistent connections kept alive (never closed)
    # max_overflow = temporary extra connections allowed under burst load
    # pool_timeout = seconds to wait for a connection before raising error
    # pool_recycle = seconds before a connection is recycled (prevents stale TCP)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800   # 30 minutes

    # ── Pydantic-Settings config ──────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",           # load from .env in the project root
        env_file_encoding="utf-8",
        case_sensitive=False,      # DB_USER == db_user
        extra="ignore",            # silently ignore unknown env vars
    )

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def database_url(self) -> str:
        """
        Builds the SQLAlchemy connection URL.
        Format: postgresql://user:password@host:port/dbname
        Matches the pattern used in load_csv_to_postgres.py for consistency.
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        """Splits the CORS_ORIGINS string into a list FastAPI can consume."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.

    @lru_cache() means Settings() is called ONCE for the entire app lifetime.
    Every subsequent call returns the same object — no repeated .env file reads.

    Usage in any file:
        from api.config import get_settings
        settings = get_settings()
    """
    return Settings()