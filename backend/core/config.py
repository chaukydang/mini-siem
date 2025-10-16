# backend/core/config.py
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Xác định đường dẫn gốc repo: mini-siem/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Ép nạp .env ở gốc repo (không ghi đè biến env đang có)
load_dotenv(PROJECT_ROOT / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        # ignore extra env keys để tránh lỗi vặt
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., description="SQLAlchemy URL for PostgreSQL")
    API_KEYS: str = "dev-key-1,dev-key-2"
    SECRET_KEY: str = "change-me"
    RATE_LIMIT_PER_MIN: int = 3000
    LOG_LEVEL: str = "INFO"
    RETENTION_DAYS: int = 14


settings = Settings()
