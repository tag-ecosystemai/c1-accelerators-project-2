import os

from llm.client import (
    GroqLLMClient,
    LLMClient,
    MockLLMClient,
)
from llm.prompts import (
    build_candidate_explanation_prompt,
    build_comparison_explanation_prompt,
)


def get_llm_client() -> LLMClient:
    """Create the configured LLM provider."""

    provider = os.getenv("LLM_PROVIDER")

    if not provider:
        raise RuntimeError(
            "LLM_PROVIDER is not configured."
        )

    provider = provider.lower()

    if provider == "groq":
        return GroqLLMClient()

    if provider == "mock":
        return MockLLMClient()

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER: {provider}"
    )

class ExplanationService:
    """Generate grounded recruiter explanations."""

    def __init__(
        self,
        client: LLMClient | None = None,
    ) -> None:
        self.client = client or get_llm_client()

        self.model = getattr(
            self.client,
            "model",
            "unknown",
        )

    def generate_candidate_explanation(
        self,
        job_profile: dict[str, object],
        candidate_profile: dict[str, object],
        match_result: dict[str, object],
        score_breakdown: dict[str, object],
    ) -> str:
        prompt = build_candidate_explanation_prompt(
            job_profile=job_profile,
            candidate_profile=candidate_profile,
            match_result=match_result,
            score_breakdown=score_breakdown,
        )

        return self.client.generate(prompt)

    def generate_comparison_explanation(
        self,
        job_profile: dict[str, object],
        candidates: list[dict[str, object]],
    ) -> str:
        prompt = build_comparison_explanation_prompt(
            job_profile=job_profile,
            candidates=candidates,
        )

        return self.client.generate(prompt)