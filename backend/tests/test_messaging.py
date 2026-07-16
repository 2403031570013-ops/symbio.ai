from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def register_user(client: TestClient) -> str:
    email = f"qa+msg-{uuid4().hex}@symbioai.io"
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "full_name": "Messaging QA",
            "password": "Password123!",
            "role": "Waste Producer",
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["token"]


def test_create_conversation_and_send_message():
    with TestClient(app) as client:
        token = register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        create_response = client.post(
            "/api/messaging/conversations",
            headers=headers,
            json={
                "match_id": "match-1",
                "material_name": "Industrial Acetic Acid Waste",
                "partner_name": "DuPont Polymer Labs",
                "message": "Can we discuss pricing and pickup timing?",
            },
        )
        assert create_response.status_code == 200
        created = create_response.json()["data"]
        conversation_id = created["conversation"]["id"]
        assert created["message"]["body"] == "Can we discuss pricing and pickup timing?"

        message_response = client.post(
            f"/api/messaging/conversations/{conversation_id}/messages",
            headers=headers,
            json={"body": "I can share the certificate PDF before shipment.", "attachment_name": "certificate.pdf", "attachment_type": "application/pdf"},
        )
        assert message_response.status_code == 200
        assert message_response.json()["data"]["message"]["attachment_name"] == "certificate.pdf"

        offer_response = client.put(
            f"/api/messaging/conversations/{conversation_id}/offer",
            headers=headers,
            json={"status": "countered", "offer_amount": "$4,200"},
        )
        assert offer_response.status_code == 200
        assert offer_response.json()["data"]["conversation"]["status"] == "offer_countered"

        list_response = client.get(f"/api/messaging/conversations/{conversation_id}/messages", headers=headers)
        assert list_response.status_code == 200
        messages = list_response.json()["data"]["messages"]
        assert len(messages) >= 3
