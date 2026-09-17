import os

import httpx


GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


class ExplanationService:
    """Generate grounded recruiter explanations using Groq."""

    def __init__(self) -> None:
        self.api_key = os.getenv(
            "GROQ_API_KEY"
        )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        )

    def _generate(
        self,
        prompt: str,
    ) -> str:
        """Send a grounded prompt to Groq and return its response."""

        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        response = httpx.post(
            GROQ_URL,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a grounded recruitment "
                            "analysis assistant."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.2,
            },
            timeout=60.0,
        )

        response.raise_for_status()

        data = response.json()

        choices = data.get("choices")

        if not isinstance(choices, list) or not choices:
            raise RuntimeError(
                "Groq returned no completion."
            )

        message = choices[0].get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "Groq returned an invalid completion."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                "Groq returned an empty explanation."
            )

        return content.strip()

    def generate_candidate_explanation(
        self,
        job_profile: dict[str, object],
        candidate_profile: dict[str, object],
        match_result: dict[str, object],
        score_breakdown: dict[str, object],
    ) -> str:
        prompt = f"""
You are explaining a deterministic candidate-matching result
to a recruiter.

The matching engine has already calculated the candidate's
score and skill matches.

You MUST NOT:
- calculate a new score
- change the ranking
- invent candidate experience
- infer protected characteristics
- make claims not supported by the supplied evidence

Explain the existing result clearly and concisely.

Job profile:
{job_profile}

Candidate profile:
{candidate_profile}

Deterministic match result:
{match_result}

Deterministic score breakdown:
{score_breakdown}

Your response should contain:
1. Overall fit explanation based only on the supplied result.
2. Key matching evidence.
3. Important skill gaps.
4. Any areas where evidence is missing or insufficient.

Use "No evidence found" when the supplied data does not
contain supporting evidence. Do not interpret missing
evidence as proof that the candidate lacks the skill.
"""

        return self._generate(prompt)

    def generate_comparison_explanation(
        self,
        job_profile: dict[str, object],
        candidates: list[dict[str, object]],
    ) -> str:
        """Generate a grounded comparison of candidate results."""

        prompt = f"""
You are explaining a deterministic candidate comparison
to a recruiter.

The matching engine has already calculated every candidate's
score, ranking, skill matches, skill gaps, evidence, and
score breakdown.

Your job is ONLY to explain the supplied comparison.

You MUST NOT:
- calculate a new score
- create a new ranking
- change the supplied ranking
- recommend a candidate
- invent candidate experience
- infer protected characteristics
- make claims not supported by the supplied evidence

Job profile:
{job_profile}

Candidate results:
{candidates}

Your response should:
1. Summarize the material differences between the candidates.
2. Identify differences in required-skill coverage.
3. Identify relevant differences in experience,
   responsibilities, education, and preferred skills.
4. Reference supporting evidence where available.
5. Identify important gaps or missing evidence.
6. Preserve the deterministic scores and ranking exactly as supplied.

Use "No evidence found" when supporting evidence is absent.
Do not interpret missing evidence as proof that a candidate
lacks a skill.

Do not declare a winner or tell the recruiter whom to select.
The recruiter remains responsible for the hiring decision.
"""

        return self._generate(prompt)