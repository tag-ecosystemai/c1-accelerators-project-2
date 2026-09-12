from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_submit_job_description_saves_job():
    response = client.post(
        "/jobs",
        json={"text": "Python Backend Engineer"},
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] > 0
    assert response_data["text"] == "Python Backend Engineer"
    assert "created_at" in response_data


def test_submit_job_description_rejects_empty_text():
    response = client.post(
        "/jobs",
        json={"text": ""},
    )

    assert response.status_code == 422