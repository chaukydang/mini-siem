# backend/core/config.py
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ✔ Default rỗng để mypy không báo missing arg,
    #   nhưng sẽ bị chặn bởi validator nếu không được set qua env/.env
    DATABASE_URL: str = Field("", description="SQLAlchemy URL for PostgreSQL")
    API_KEYS: str = "dev-key-1,dev-key-2"
    SECRET_KEY: str = "change-me"
    RATE_LIMIT_PER_MIN: int = 3000
    LOG_LEVEL: str = "INFO"
    RETENTION_DAYS: int = 14

    @field_validator("DATABASE_URL")
    @classmethod
    def _require_db_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL is required. Set it via environment or .env")
        return v


settings = Settings()
