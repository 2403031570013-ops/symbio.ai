from pathlib import Path
from typing import Any, List

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    PROJECT_NAME: str = "SymbioAI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = Field(default="change-me-in-production", validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"))
    JWT_REFRESH_SECRET: str = Field(default="change-me-refresh-in-production", validation_alias=AliasChoices("JWT_REFRESH_SECRET"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = Field(default="mongodb+srv://user:pass@cluster.mongodb.net/symbioai?retryWrites=true&w=majority", validation_alias=AliasChoices("DATABASE_URL", "MONGODB_URI"))
    DATABASE_NAME: str = "symbioai"
    CORS_ORIGINS: str = ""
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    RESEND_API_KEY: str | None = None
    DEV_EMAIL_OTP: str = "654321"
    DEV_MOBILE_OTP: str = "123456"
    DEV_FACTORY_CODE: str = "123456"
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
    CLOUD_STORAGE_KEYS: str | None = None
    OPENAI_API_KEY: str | None = None
    FACTORY_VERIFICATION_CODE: str | None = None
    FRONTEND_URL: str = "http://localhost:5173"
    RATE_LIMIT_PER_MINUTE: int = 120

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def validate_production_secrets(self) -> None:
        if self.ENVIRONMENT.lower() != "production":
            return
        if self.SECRET_KEY == "change-me-in-production" or len(self.SECRET_KEY) < 32:
            raise RuntimeError("JWT_SECRET/SECRET_KEY must be a unique value of at least 32 characters in production")
        if self.JWT_REFRESH_SECRET == "change-me-refresh-in-production" or len(self.JWT_REFRESH_SECRET) < 32:
            raise RuntimeError("JWT_REFRESH_SECRET must be configured in production")
        if not self.DATABASE_URL or "user:pass" in self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL must be configured with valid credentials in production")
        if self.CORS_ORIGINS:
            if "YOUR_" in self.CORS_ORIGINS or any(not origin.startswith("https://") for origin in self.cors_origins):
                raise RuntimeError("CORS_ORIGINS must contain only explicit HTTPS frontend origins in production")
        if not self.FRONTEND_URL.startswith("https://") or "YOUR_" in self.FRONTEND_URL:
            raise RuntimeError("FRONTEND_URL must be an explicit HTTPS URL in production")
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
            raise RuntimeError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured in production")
        if not self.RESEND_API_KEY:
            raise RuntimeError("RESEND_API_KEY must be configured in production")
        if not self.FACTORY_VERIFICATION_CODE:
            raise RuntimeError("FACTORY_VERIFICATION_CODE must be configured in production")

    @property
    def MONGODB_URI(self) -> str:
        return self.DATABASE_URL


settings = Settings()

