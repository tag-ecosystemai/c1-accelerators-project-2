import pytest

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

ANONYMOUS_SCREENING_COOKIE = (
    "talentmatch_anonymous_screening"
)


def register_user(
    name: str = "Test Recruiter",
    email: str = "recruiter@example.com",
    password: str = "password123",
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201


def create_job(
    text: str = "Python Backend Engineer",
) -> int:
    response = client.post(
        "/jobs",
        json={"text": text},
    )

    assert response.status_code == 201

    return response.json()["job"]["id"]


def clear_anonymous_screening_cookie() -> None:
    client.cookies.delete(
        ANONYMOUS_SCREENING_COOKIE
    )


@pytest.fixture(autouse=True)
def authenticated_user():
    """Authenticate each test with a fresh user."""

    clear_anonymous_screening_cookie()

    register_user()

    yield

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()


def test_submit_job_description_saves_job():
    job_id = create_job()

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 200
    assert response.json()["text"] == (
        "Python Backend Engineer"
    )


def test_submit_job_description_automatically_creates_profile():
    job_id = create_job(
        """
        Backend Engineer

        Required Skills
        - Python
        - FastAPI

        Preferred Skills
        - Docker

        Responsibilities
        - Build backend services

        Education
        - Bachelor's degree in Computer Science

        Requirements
        - Minimum 3 years of experience
        """
    )

    response = client.get(
        f"/jobs/{job_id}/profile"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["job_id"] == job_id
    assert body["title"] == "Backend Engineer"

    required_skills = {
        skill["normalized_name"]
        for skill in body["required_skills"]
    }

    preferred_skills = {
        skill["normalized_name"]
        for skill in body["preferred_skills"]
    }

    assert "python" in required_skills
    assert "fastapi" in required_skills
    assert "docker" in preferred_skills

    assert body["minimum_experience_years"] == 3.0
    assert body["responsibilities"] == [
        "Build backend services"
    ]

    assert body["education_requirements"] == [
        "Bachelor's degree in Computer Science"
    ]


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
    ],
)
def test_submit_job_description_rejects_blank_text(
    text: str,
):
    response = client.post(
        "/jobs",
        json={"text": text},
    )

    assert response.status_code == 422


def test_submit_job_description_rejects_text_over_fifty_thousand_characters():
    response = client.post(
        "/jobs",
        json={
            "text": "a" * 50_001
        },
    )

    assert response.status_code == 422


def test_get_job_description_rejects_unknown_id():
    response = client.get(
        "/jobs/999999"
    )

    assert response.status_code == 404


def test_list_job_descriptions_returns_only_data_created_in_this_test():
    create_job()

    response = client.get("/jobs")

    assert response.status_code == 200

    jobs = response.json()["jobs"]

    assert len(jobs) == 1
    assert jobs[0]["text"] == (
        "Python Backend Engineer"
    )


def test_job_creation_response_contains_job_and_profile():
    response = client.post(
        "/jobs",
        json={
            "text": """
            Backend Engineer

            Required Skills
            - Python
            - FastAPI
            """
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "job" in body
    assert "profile" in body

    assert body["job"]["id"] == body["profile"]["job_id"]
    assert body["profile"]["title"] == "Backend Engineer"


def test_create_job_profile_endpoint_no_longer_exists():
    job_id = create_job()

    response = client.post(
        f"/jobs/{job_id}/profile",
        json={},
    )

    assert response.status_code == 405


def test_get_job_profile_rejects_unknown_profile():
    response = client.get(
        "/jobs/999999/profile"
    )

    assert response.status_code == 404


def test_users_cannot_access_another_users_job():
    job_id = create_job()

    client.post("/auth/logout")

    register_user(
        name="Second Recruiter",
        email="second@example.com",
        password="password123",
    )

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 404


def test_users_cannot_see_another_users_jobs():
    create_job()

    client.post("/auth/logout")

    register_user(
        name="Second Recruiter",
        email="second@example.com",
        password="password123",
    )

    response = client.get("/jobs")

    assert response.status_code == 200
    assert response.json()["jobs"] == []


def test_unauthenticated_user_can_create_anonymous_job():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    response = client.post(
        "/jobs",
        json={
            "text": "Python Backend Engineer"
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["job"]["id"] == body["profile"]["job_id"]

    assert (
        ANONYMOUS_SCREENING_COOKIE
        in client.cookies
    )


def test_anonymous_job_can_be_accessed_with_screening_cookie():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_anonymous_job_profile_can_be_accessed_with_screening_cookie():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job(
        """
        Backend Engineer

        Required Skills
        - Python
        - FastAPI
        """
    )

    response = client.get(
        f"/jobs/{job_id}/profile"
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id


def test_anonymous_user_cannot_access_job_without_screening_cookie():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    clear_anonymous_screening_cookie()

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 404


def test_anonymous_user_cannot_access_another_anonymous_job():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    first_job_id = create_job(
        "First Python Backend Engineer"
    )

    clear_anonymous_screening_cookie()

    second_job_id = create_job(
        "Second Python Backend Engineer"
    )

    response = client.get(
        f"/jobs/{first_job_id}"
    )

    assert response.status_code == 404

    response = client.get(
        f"/jobs/{second_job_id}"
    )

    assert response.status_code == 200


def test_anonymous_user_cannot_access_authenticated_job():
    authenticated_job_id = create_job()

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    response = client.get(
        f"/jobs/{authenticated_job_id}"
    )

    assert response.status_code == 404


def test_unauthenticated_user_cannot_list_jobs():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    response = client.get("/jobs")

    assert response.status_code == 401


def test_anonymous_jobs_are_not_returned_in_history():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    anonymous_response = client.post(
        "/jobs",
        json={
            "text": "Anonymous Python Engineer"
        },
    )

    assert anonymous_response.status_code == 201

    anonymous_job_id = (
        anonymous_response.json()["job"]["id"]
    )

    clear_anonymous_screening_cookie()

    register_user(
        name="History Recruiter",
        email="history@example.com",
        password="password123",
    )

    authenticated_job_id = create_job(
        "Authenticated Python Engineer"
    )

    response = client.get("/jobs")

    assert response.status_code == 200

    jobs = response.json()["jobs"]
    job_ids = {job["id"] for job in jobs}

    assert authenticated_job_id in job_ids
    assert anonymous_job_id not in job_ids


def test_job_profile_preserves_skill_evidence():
    job_id = create_job(
        """
        Backend Engineer

        Required Skills
        - Python
        - FastAPI

        Preferred Skills
        - PostgreSQL
        """
    )

    response = client.get(
        f"/jobs/{job_id}/profile"
    )

    assert response.status_code == 200

    body = response.json()

    python_skill = next(
        skill
        for skill in body["required_skills"]
        if skill["normalized_name"] == "python"
    )

    assert python_skill["required"] is True
    assert python_skill["evidence"]
    assert python_skill["evidence"][0]["text"]


def test_upload_job_description_txt_file():
    content = b"""Backend Engineer

Required Skills
- Python
- FastAPI

Preferred Skills
- Docker
"""

    response = client.post(
        "/jobs/upload",
        files={
            "file": (
                "job-description.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["job"]["text"].strip() == content.decode().strip()
    assert body["profile"]["job_id"] == body["job"]["id"]

    required_skills = {
        skill["normalized_name"]
        for skill in body["profile"]["required_skills"]
    }

    preferred_skills = {
        skill["normalized_name"]
        for skill in body["profile"]["preferred_skills"]
    }

    assert "python" in required_skills
    assert "fastapi" in required_skills
    assert "docker" in preferred_skills


def test_unauthenticated_user_can_upload_anonymous_job_description():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    content = b"""Backend Engineer

Required Skills
- Python
- FastAPI
"""

    response = client.post(
        "/jobs/upload",
        files={
            "file": (
                "job-description.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["job"]["text"].strip() == content.decode().strip()
    assert body["profile"]["job_id"] == body["job"]["id"]

    assert (
        ANONYMOUS_SCREENING_COOKIE
        in client.cookies
    )


def test_upload_job_description_rejects_unsupported_file_type():
    response = client.post(
        "/jobs/upload",
        files={
            "file": (
                "job-description.jpg",
                b"not a supported job description",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported file type. "
        "Supported formats: PDF, DOCX, TXT."
    )


def test_upload_job_description_rejects_empty_file():
    response = client.post(
        "/jobs/upload",
        files={
            "file": (
                "job-description.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The uploaded job description is empty."
    )


def test_upload_job_description_rejects_unextractable_file():
    response = client.post(
        "/jobs/upload",
        files={
            "file": (
                "job-description.txt",
                b"   ",
                "text/plain",
            )
        },
    )

    assert response.status_code == 422