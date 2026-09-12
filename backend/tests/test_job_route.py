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

def test_get_job_description_returns_saved_job():
    created_response = client.post(
        "/jobs",
        json={"text": "Python Backend Engineer"},
    )

    job_id = created_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["text"] == "Python Backend Engineer"


def test_get_job_description_rejects_unknown_id():
    response = client.get("/jobs/999999")

    assert response.status_code == 404

def test_list_job_descriptions_returns_saved_jobs():
    client.post(
        "/jobs",
        json={"text": "Python Backend Engineer"},
    )

    response = client.get("/jobs")

    assert response.status_code == 200
    assert len(response.json()["jobs"]) >= 1