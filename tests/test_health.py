from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "quantic-project-3-hr-agent"


def test_chat_pto_request():
    response = client.post(
        "/chat",
        json={
            "message": "Can employee E1001 take three days of PTO next week?",
            "employee_id": "E1001",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "citations" in data
    assert "snippets" in data
    assert "tool_trace" in data
    assert len(data["tool_trace"]) >= 2