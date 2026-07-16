from pathlib import Path
from typing import Any, List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_URL = f"sqlite:///{(BACKEND_DIR / 'symbioai.db').as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    PROJECT_NAME: str = "SymbioAI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = DEFAULT_SQLITE_URL
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5176,http://127.0.0.1:5173"
    GOOGLE_CLIENT_ID: str | None = None
    RESEND_API_KEY: str | None = None
    ENVIRONMENT: str = "development"
    SECURE_COOKIES: bool = False
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@symbioai.com"
    SMTP_USE_TLS: bool = True
    STORAGE_PROVIDER: str = "s3"
    S3_BUCKET: str | None = None
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_ENDPOINT_URL: str | None = None
    S3_PUBLIC_BASE_URL: str | None = None
    FRONTEND_URL: str = "http://localhost:5173"
    RATE_LIMIT_PER_MINUTE: int = 120

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    def validate_production_secrets(self) -> None:
        if self.ENVIRONMENT.lower() != "production":
            return
        if self.SECRET_KEY == "change-me-in-production" or len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY must be a unique value of at least 32 characters in production")
        if self.DATABASE_URL.startswith("sqlite"):
            raise RuntimeError("DATABASE_URL must point to a managed database in production")
        if not self.CORS_ORIGINS or "YOUR_" in self.CORS_ORIGINS or any(not origin.startswith("https://") for origin in self.cors_origins):
            raise RuntimeError("CORS_ORIGINS must contain explicit HTTPS frontend origins in production")
        if not self.FRONTEND_URL.startswith("https://") or "YOUR_" in self.FRONTEND_URL:
            raise RuntimeError("FRONTEND_URL must be an explicit HTTPS URL in production")
        if not self.RESEND_API_KEY:
            raise RuntimeError("RESEND_API_KEY must be configured in production")


settings = Settings()
