import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def profile_payload() -> dict[str, object]:
    evidence = {
        "text": "The candidate must know Python and FastAPI.",
        "location": "requirements",
    }
    return {
        "title": "Backend Engineer",
        "required_skills": [
            {"name": "Python", "normalized_name": "python", "required": True, "evidence": [evidence]},
            {"name": "FastAPI", "normalized_name": "fastapi", "required": True, "evidence": [evidence]},
        ],
        "preferred_skills": [
            {"name": "PostgreSQL", "normalized_name": "postgresql", "required": False, "evidence": [evidence]}
        ],
        "minimum_experience_years": 3.0,
        "education_requirements": ["Bachelor's degree in Computer Science"],
        "responsibilities": ["Build backend services"],
        "evidence": [evidence],
    }


def create_job() -> int:
    response = client.post("/jobs", json={"text": "Python Backend Engineer"})
    assert response.status_code == 201
    return response.json()["id"]


def test_submit_job_description_saves_job():
    job_id = create_job()
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["text"] == "Python Backend Engineer"


@pytest.mark.parametrize("text", ["", "   "])
def test_submit_job_description_rejects_blank_text(text: str):
    assert client.post("/jobs", json={"text": text}).status_code == 422


def test_submit_job_description_rejects_text_over_fifty_thousand_characters():
    assert client.post("/jobs", json={"text": "a" * 50_001}).status_code == 422


def test_get_job_description_rejects_unknown_id():
    assert client.get("/jobs/999999").status_code == 404


def test_list_job_descriptions_returns_only_data_created_in_this_test():
    create_job()
    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 1


def test_create_job_profile_preserves_canonical_structures():
    job_id = create_job()
    response = client.post(f"/jobs/{job_id}/profile", json=profile_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["job_id"] == job_id
    assert body["required_skills"][0]["normalized_name"] == "python"
    assert body["required_skills"][0]["evidence"][0]["location"] == "requirements"
    assert body["evidence"][0]["text"].startswith("The candidate")
    assert "raw_text" not in body


def test_create_job_profile_rejects_nonexistent_job():
    response = client.post("/jobs/999999/profile", json=profile_payload())
    assert response.status_code == 404


def test_create_job_profile_rejects_duplicate_profile():
    job_id = create_job()
    assert client.post(f"/jobs/{job_id}/profile", json=profile_payload()).status_code == 201
    assert client.post(f"/jobs/{job_id}/profile", json=profile_payload()).status_code == 409


def test_get_job_profile_returns_saved_profile():
    job_id = create_job()
    client.post(f"/jobs/{job_id}/profile", json=profile_payload())
    response = client.get(f"/jobs/{job_id}/profile")
    assert response.status_code == 200
    assert response.json()["minimum_experience_years"] == 3.0


def test_get_job_profile_rejects_unknown_profile():
    assert client.get("/jobs/999999/profile").status_code == 404
