from app.core.config import Settings


def test_cors_origins_accept_comma_separated_env_values():
    settings = Settings(CORS_ORIGINS="https://app.example.com, https://admin.example.com")
    assert settings.cors_origins == ["https://app.example.com", "https://admin.example.com"]


def test_postgres_url_is_normalized_for_psycopg_driver():
    settings = Settings(DATABASE_URL="postgres://user:pass@localhost:5432/symbioai")
    assert settings.DATABASE_URL == "postgresql+psycopg://user:pass@localhost:5432/symbioai"


def test_production_rejects_default_secret():
    settings = Settings(ENVIRONMENT="production", SECRET_KEY="change-me-in-production")
    try:
        settings.validate_production_secrets()
    except RuntimeError as exc:
        assert "SECRET_KEY" in str(exc)
    else:
        raise AssertionError("production settings accepted the default secret")
