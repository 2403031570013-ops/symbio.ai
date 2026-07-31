from app.core.config import Settings


def test_cors_origins_accept_comma_separated_env_values():
    settings = Settings(CORS_ORIGINS="https://app.example.com, https://admin.example.com")
    assert settings.cors_origins == ["https://app.example.com", "https://admin.example.com"]


def test_mongodb_uri_defaults_to_symbioai_database():
    settings = Settings(MONGODB_URI="mongodb+srv://user:pass@cluster0.mongodb.net/symbioai?retryWrites=true&w=majority")
    assert "symbioai" in settings.MONGODB_URI


def test_production_rejects_default_secret():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="change-me-in-production",
        JWT_REFRESH_SECRET="r" * 32,
        DATABASE_URL="mongodb+srv://prod:prod@cluster0.mongodb.net/symbioai",
        CORS_ORIGINS="https://app.example.com",
        FRONTEND_URL="https://app.example.com",
        GOOGLE_CLIENT_ID="client-id",
        GOOGLE_CLIENT_SECRET="client-secret",
        RESEND_API_KEY="resend-key",
        FACTORY_VERIFICATION_CODE="factory-code",
    )
    try:
        settings.validate_production_secrets()
    except RuntimeError as exc:
        assert "JWT_SECRET" in str(exc)
    else:
        raise AssertionError("production settings accepted the default secret")
