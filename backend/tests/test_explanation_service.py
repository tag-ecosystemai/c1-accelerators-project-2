import pytest

from backend.app.services.explanations import (
    ExplanationService,
    get_llm_client,
)
from llm.client import MockLLMClient


def test_get_llm_client_requires_provider(monkeypatch):
    monkeypatch.delenv(
        "LLM_PROVIDER",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="LLM_PROVIDER is not configured",
    ):
        get_llm_client()

def test_explanation_service_uses_injected_client():
    client = MockLLMClient()
    service = ExplanationService(client=client)

    assert service.client is client
    assert service.model == "mock-llm"


def test_candidate_explanation_uses_llm_client():
    client = MockLLMClient()
    service = ExplanationService(client=client)

    result = service.generate_candidate_explanation(
        job_profile={
            "title": "Backend Engineer",
        },
        candidate_profile={
            "name": "Test Candidate",
        },
        match_result={
            "matched_skills": ["Python"],
        },
        score_breakdown={
            "required_skills": 40,
        },
    )

    assert isinstance(result, str)
    assert result
    assert "deterministic matching results" in result


def test_comparison_explanation_uses_llm_client():
    client = MockLLMClient()
    service = ExplanationService(client=client)

    result = service.generate_comparison_explanation(
        job_profile={
            "title": "Backend Engineer",
        },
        candidates=[
            {
                "candidate_id": 1,
                "overall_score": 85,
            },
            {
                "candidate_id": 2,
                "overall_score": 78,
            },
        ],
    )

    assert isinstance(result, str)
    assert result
    assert "deterministic matching results" in result