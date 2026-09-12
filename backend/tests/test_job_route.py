from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_submit_job_description_returns_validated_input():
    response = client.post(
        "/jobs",
        json={"text": "Python Backend Engineer"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "text": "Python Backend Engineer",
    }


def test_submit_job_description_rejects_empty_text():
    response = client.post(
        "/jobs",
        json={"text": ""},
    )

    assert response.status_code == 422