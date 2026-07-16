from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.api.v1.endpoints import auth as auth_endpoint


def test_resend_otp_verification_flow(monkeypatch):
    email = f"otp+{uuid4().hex}@symbioai.io"
    monkeypatch.setattr(settings, "RESEND_API_KEY", "test-key")
    monkeypatch.setattr(auth_endpoint.secrets, "randbelow", lambda _: 123456)
    monkeypatch.setattr(auth_endpoint, "send_resend_verification_otp", lambda *_: None)

    with TestClient(app) as client:
        register = client.post("/api/auth/register", json={
            "email": email,
            "full_name": "OTP QA User",
            "password": "Password123!",
            "role": "Waste Producer",
        })
        assert register.status_code == 200

        sent = client.post("/api/auth/send-otp", json={"email": email})
        assert sent.status_code == 200
        assert sent.json()["data"]["expires_in_seconds"] == 300

        verified = client.post("/api/auth/verify-otp", json={"email": email, "otp": "123456"})
        assert verified.status_code == 200
        assert verified.json()["data"]["verified"] is True

        reused = client.post("/api/auth/verify-otp", json={"email": email, "otp": "123456"})
        assert reused.status_code == 400


def test_otp_resend_cooldown(monkeypatch):
    email = f"otp-cooldown+{uuid4().hex}@symbioai.io"
    monkeypatch.setattr(settings, "RESEND_API_KEY", "test-key")
    monkeypatch.setattr(auth_endpoint, "send_resend_verification_otp", lambda *_: None)

    with TestClient(app) as client:
        client.post("/api/auth/register", json={
            "email": email,
            "full_name": "OTP Cooldown QA",
            "password": "Password123!",
            "role": "Waste Producer",
        })
        assert client.post("/api/auth/send-otp", json={"email": email}).status_code == 200
        assert client.post("/api/auth/send-otp", json={"email": email}).status_code == 429
