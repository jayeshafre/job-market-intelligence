"""
api/config.py
=============
Centralized application configuration.

All environment variables are read ONCE from the .env file here.
Every other file imports from this module — never from os.getenv() directly.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ── Project Root / .env Path ────────────────────────────────────────────────
# config.py → backend/api/config.py
# parent         = api
# parent.parent  = backend
# parent.parent.parent = project root

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.
    Field names MUST match your .env variable names exactly (case-insensitive).
    """

    # ── Database ──────────────────────────────────────────────────────────
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "TIGER"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "job_market_db"

    # ── Application ───────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"

    APP_TITLE: str = "Job Market Intelligence API"

    APP_DESCRIPTION: str = (
        "AI-Powered Global Job Market Intelligence & Workforce Analytics Platform"
    )

    # ── AI / Groq ─────────────────────────────────────────────────────────
    # REQUIRED: app crashes at startup if missing
    GROQ_API_KEY: str

    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173"
    )

    # ── SQLAlchemy Connection Pool ────────────────────────────────────────
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL_SECONDS: int = 3600  # conversations expire after 1 hour

    # ── Pydantic Settings Config ─────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Computed Properties ───────────────────────────────────────────────

    @property
    def database_url(self) -> str:
        """
        PostgreSQL connection URL for SQLAlchemy.
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Converts comma-separated CORS origins into a Python list.
        """
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
        ]


# ── Singleton Settings Instance ─────────────────────────────────────────────

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached application settings.

    Settings() is created only once for the entire app lifecycle.
    """

    settings = Settings()

    # Optional startup debug logs
    print(f"Loaded ENV file: {ENV_FILE}")
    print(f"GROQ_API_KEY loaded: {bool(settings.GROQ_API_KEY)}")

    return settings