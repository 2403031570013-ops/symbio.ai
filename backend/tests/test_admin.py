from fastapi.testclient import TestClient

from app.main import app


def admin_headers(client: TestClient) -> dict:
    response = client.post("/api/auth/admin-login", json={"email": "admin@symbioai.com", "password": "Admin@123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['token']}"}


def test_admin_dashboard_health_and_export():
    with TestClient(app) as client:
        headers = admin_headers(client)

        dashboard = client.get("/api/admin/dashboard", headers=headers)
        assert dashboard.status_code == 200
        assert "users" in dashboard.json()["data"]["stats"]

        health = client.get("/api/admin/system-health", headers=headers)
        assert health.status_code == 200
        assert health.json()["data"]["database"]["status"] == "healthy"

        export = client.get("/api/admin/export/users.csv", headers=headers)
        assert export.status_code == 200
        assert "email" in export.text


def test_non_admin_cannot_access_admin_dashboard():
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={"email": "not-admin@symbioai.io", "full_name": "Not Admin", "password": "Password123!", "role": "Waste Producer"},
        )
        assert response.status_code in {200, 400}
        login = client.post("/api/auth/login", json={"email": "not-admin@symbioai.io", "password": "Password123!"})
        token = login.json()["data"]["token"]
        denied = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert denied.status_code == 403
