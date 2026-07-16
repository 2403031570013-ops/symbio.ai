from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_flow():
    email = f'qa+{uuid4().hex}@symbioai.io'

    with TestClient(app) as client:
        register_response = client.post('/api/auth/register', json={
            'email': email,
            'full_name': 'QA User',
            'password': 'Password123!',
            'role': 'Waste Producer',
        })
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert register_data['success'] is True
        assert register_data['data']['token']
        assert register_data['data']['user']['email'] == email

        login_response = client.post('/api/auth/login', json={
            'email': email,
            'password': 'Password123!',
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data['success'] is True
        assert login_data['data']['token']


def test_google_login_requires_real_credential():
    with TestClient(app) as client:
        response = client.post('/api/auth/google', json={
            'email': 'google.user@symbioai.local',
            'full_name': 'Google Demo User',
        })
        assert response.status_code == 400
        assert response.json()['detail'] == 'A valid Google credential is required'
