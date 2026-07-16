import pyotp
from fastapi.testclient import TestClient

from app.main import app


def test_two_factor_setup_enable_and_disable():
    with TestClient(app) as client:
        register = client.post(
            "/api/auth/register",
            json={"email": "two-factor@symbioai.io", "full_name": "Two Factor", "password": "Password123!", "role": "Waste Producer"},
        )
        assert register.status_code in {200, 400}
        login = client.post("/api/auth/login", json={"email": "two-factor@symbioai.io", "password": "Password123!"})
        token = login.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        setup = client.post("/api/auth/2fa/setup", headers=headers)
        assert setup.status_code == 200
        secret = setup.json()["data"]["secret"]
        code = pyotp.TOTP(secret).now()

        enabled = client.post("/api/auth/2fa/enable", headers=headers, json={"code": code})
        assert enabled.status_code == 200
        assert len(enabled.json()["data"]["recovery_codes"]) == 8

        disabled = client.post("/api/auth/2fa/disable", headers=headers, json={"code": pyotp.TOTP(secret).now()})
        assert disabled.status_code == 200


def test_storage_presign_requires_provider_configuration():
    with TestClient(app) as client:
        register = client.post(
            "/api/auth/register",
            json={"email": "storage-check@symbioai.io", "full_name": "Storage Check", "password": "Password123!", "role": "Waste Producer"},
        )
        assert register.status_code in {200, 400}
        login = client.post("/api/auth/login", json={"email": "storage-check@symbioai.io", "password": "Password123!"})
        token = login.json()["data"]["token"]
        response = client.post(
            "/api/storage/presign",
            headers={"Authorization": f"Bearer {token}"},
            json={"filename": "certificate.pdf", "content_type": "application/pdf", "purpose": "certificates"},
        )
        assert response.status_code == 503
        assert "S3-compatible storage is not configured" in response.json()["detail"]
