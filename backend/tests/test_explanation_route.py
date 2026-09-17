from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

ANONYMOUS_SCREENING_COOKIE = (
    "talentmatch_anonymous_screening"
)


def register_user(
    name: str = "Test Recruiter",
    email: str = "explanation@example.com",
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


def clear_anonymous_screening_cookie() -> None:
    client.cookies.delete(
        ANONYMOUS_SCREENING_COOKIE
    )


def create_job() -> int:
    response = client.post(
        "/jobs",
        json={
            "text": """
            Backend Engineer

            Required Skills
            - Python
            - FastAPI

            Preferred Skills
            - Docker

            Responsibilities
            - Build backend services
            """
        },
    )

    assert response.status_code == 201

    return response.json()["job"]["id"]


def create_candidate(
    job_id: int,
    filename: str,
    text: str,
) -> int:
    response = client.post(
        f"/jobs/{job_id}/resumes",
        files={
            "resumes": (
                filename,
                text.encode("utf-8"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    candidates = response.json()["candidates"]

    assert len(candidates) == 1

    return candidates[0]["candidate"]["id"]


def test_candidate_explanation_uses_groq_service_without_real_api_call():
    register_user()

    job_id = create_job()

    candidate_id = create_candidate(
        job_id,
        "candidate.txt",
        """
        John Doe

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer

        Responsibilities
        Build backend services
        """,
    )

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ) as mock_service:
        mock_service.return_value.model = (
            "openai/gpt-oss-20b"
        )

        mock_service.return_value.generate_candidate_explanation.return_value = (
            "The candidate demonstrates evidence of "
            "Python, FastAPI, and backend experience."
        )

        response = client.get(
            f"/jobs/{job_id}/candidates/"
            f"{candidate_id}/explanation"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_id"] == candidate_id
    assert body["model"] == "openai/gpt-oss-20b"
    assert "Python" in body["explanation"]

    mock_service.return_value.generate_candidate_explanation.assert_called_once()

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()


def test_candidate_comparison_explanation_uses_groq_service_without_real_api_call():
    register_user(
        email="comparison@example.com"
    )

    job_id = create_job()

    candidate_one = create_candidate(
        job_id,
        "candidate-one.txt",
        """
        Alice

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer

        Responsibilities
        Build backend services
        """,
    )

    candidate_two = create_candidate(
        job_id,
        "candidate-two.txt",
        """
        Bob

        Skills
        Python

        Experience
        Software Developer
        """,
    )

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ) as mock_service:
        mock_service.return_value.model = (
            "openai/gpt-oss-20b"
        )

        mock_service.return_value.generate_comparison_explanation.return_value = (
            "The supplied results show differences "
            "in required skill coverage and experience."
        )

        response = client.post(
            f"/jobs/{job_id}/candidates/"
            "compare/explanation",
            json={
                "candidate_ids": [
                    candidate_one,
                    candidate_two,
                ]
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_ids"] == [
        candidate_one,
        candidate_two,
    ]

    assert body["model"] == "openai/gpt-oss-20b"

    assert (
        "required skill coverage"
        in body["explanation"]
    )

    mock_service.return_value.generate_comparison_explanation.assert_called_once()

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()


def test_anonymous_candidate_explanation_is_allowed():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    candidate_id = create_candidate(
        job_id,
        "anonymous-candidate.txt",
        """
        Anonymous Candidate

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer

        Responsibilities
        Build backend services
        """,
    )

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ) as mock_service:
        mock_service.return_value.model = (
            "openai/gpt-oss-20b"
        )

        mock_service.return_value.generate_candidate_explanation.return_value = (
            "The candidate demonstrates relevant "
            "backend experience."
        )

        response = client.get(
            f"/jobs/{job_id}/candidates/"
            f"{candidate_id}/explanation"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_id"] == candidate_id
    assert body["model"] == "openai/gpt-oss-20b"
    assert "backend experience" in body["explanation"]

    mock_service.return_value.generate_candidate_explanation.assert_called_once()


def test_anonymous_comparison_explanation_is_allowed():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    candidate_one = create_candidate(
        job_id,
        "candidate-one.txt",
        """
        Alice

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer
        """,
    )

    candidate_two = create_candidate(
        job_id,
        "candidate-two.txt",
        """
        Bob

        Skills
        Python

        Experience
        Software Developer
        """,
    )

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ) as mock_service:
        mock_service.return_value.model = (
            "openai/gpt-oss-20b"
        )

        mock_service.return_value.generate_comparison_explanation.return_value = (
            "The candidates have different "
            "skill coverage."
        )

        response = client.post(
            f"/jobs/{job_id}/candidates/"
            "compare/explanation",
            json={
                "candidate_ids": [
                    candidate_one,
                    candidate_two,
                ]
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_ids"] == [
        candidate_one,
        candidate_two,
    ]

    assert body["model"] == "openai/gpt-oss-20b"

    mock_service.return_value.generate_comparison_explanation.assert_called_once()


def test_comparison_explanation_requires_two_candidates():
    register_user(
        email="minimum-comparison@example.com"
    )

    job_id = create_job()

    candidate_id = create_candidate(
        job_id,
        "candidate.txt",
        """
        Candidate

        Skills
        Python
        """,
    )

    response = client.post(
        f"/jobs/{job_id}/candidates/"
        "compare/explanation",
        json={
            "candidate_ids": [candidate_id]
        },
    )

    assert response.status_code == 422

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()


def test_comparison_explanation_rejects_unknown_candidate():
    register_user(
        email="unknown-candidate@example.com"
    )

    job_id = create_job()

    candidate_id = create_candidate(
        job_id,
        "candidate.txt",
        """
        Candidate

        Skills
        Python
        """,
    )

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ):
        response = client.post(
            f"/jobs/{job_id}/candidates/"
            "compare/explanation",
            json={
                "candidate_ids": [
                    candidate_id,
                    999999,
                ]
            },
        )

    assert response.status_code == 404

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()


def test_authenticated_job_comparison_explanation_requires_authentication():
    register_user(
        email="authenticated-job@example.com"
    )

    job_id = create_job()

    candidate_one = create_candidate(
        job_id,
        "candidate-one.txt",
        """
        Candidate One

        Skills
        Python
        """,
    )

    candidate_two = create_candidate(
        job_id,
        "candidate-two.txt",
        """
        Candidate Two

        Skills
        FastAPI
        """,
    )

    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    with patch(
        "backend.app.routes.explanations.ExplanationService"
    ):
        response = client.post(
            f"/jobs/{job_id}/candidates/"
            "compare/explanation",
            json={
                "candidate_ids": [
                    candidate_one,
                    candidate_two,
                ]
            },
        )

    assert response.status_code == 404
    
def test_candidate_explanation_works_with_mock_llm():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    candidate_id = create_candidate(
        job_id,
        "mock-candidate.txt",
        """
        Mock Candidate

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer

        Responsibilities
        Build backend services
        """,
    )

    with patch.dict(
        "os.environ",
        {"LLM_PROVIDER": "mock"},
    ):
        response = client.get(
            f"/jobs/{job_id}/candidates/"
            f"{candidate_id}/explanation"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_id"] == candidate_id
    assert body["model"] == "mock-llm"
    assert body["explanation"]
    assert (
        "deterministic matching results"
        in body["explanation"]
    )


def test_comparison_explanation_works_with_mock_llm():
    client.post("/auth/logout")
    clear_anonymous_screening_cookie()

    job_id = create_job()

    candidate_one = create_candidate(
        job_id,
        "mock-candidate-one.txt",
        """
        Candidate One

        Skills
        Python
        FastAPI

        Experience
        Backend Engineer
        """,
    )

    candidate_two = create_candidate(
        job_id,
        "mock-candidate-two.txt",
        """
        Candidate Two

        Skills
        Python

        Experience
        Software Developer
        """,
    )

    with patch.dict(
        "os.environ",
        {"LLM_PROVIDER": "mock"},
    ):
        response = client.post(
            f"/jobs/{job_id}/candidates/"
            "compare/explanation",
            json={
                "candidate_ids": [
                    candidate_one,
                    candidate_two,
                ]
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["candidate_ids"] == [
        candidate_one,
        candidate_two,
    ]
    assert body["model"] == "mock-llm"
    assert body["explanation"]
    assert (
        "deterministic matching results"
        in body["explanation"]
    )