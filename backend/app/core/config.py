import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    REDIS_URL: str = "redis://localhost:6379/0"
    TEMP_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "tmp")
    MAX_DOWNLOAD_BYTES: int = 524_288_000  # 500 MB
    MAX_MEDIA_DURATION_SECONDS: int = 3600  # 1 hour
    JOB_TTL_SECONDS: int = 3600  # 1 hour
    FILE_RETENTION_SECONDS: int = 900  # 15 minutes
    ANALYSIS_TIMEOUT_SECONDS: int = 30
    DOWNLOAD_TIMEOUT_SECONDS: int = 600
    MAX_CONCURRENT_DOWNLOADS: int = 4
    RATE_LIMIT_PER_MINUTE: int = 30
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

settings = Settings()

# Ensure temp directory exists
os.makedirs(settings.TEMP_DIR, exist_ok=True)

