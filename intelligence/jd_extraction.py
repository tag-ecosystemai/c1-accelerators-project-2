"""
TalentMatch AI — Job Description Extraction Pipeline
Owner: Monday Imeobong (NLP / Information Extraction & Skill Intelligence Engineer)

raw JD text -> JobProfile (schemas.py), using Groq (openai/gpt-oss-20b) for
the parts that genuinely benefit from language understanding, always
validated against the schema before being trusted downstream.

Reliability (PRD §22): if Groq is unavailable, this module must not drop the
JD entirely — it degrades to a heading/bullet-point rule extractor instead
of raising up to the API layer.
"""

from __future__ import annotations

import json
import os
import re
from typing import Optional, Protocol

from intelligence.normalization import normalize_skill_list
from backend.app.schemas import JobProfile


# ---------------------------------------------------------------------------
# LLM client abstraction
# ---------------------------------------------------------------------------
# Behind a Protocol so this module is testable without hitting Groq, and so
# Souley can swap in whatever client wrapper the backend settles on.

class LLMClient(Protocol):
    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text response (expected to be a JSON string)."""
        ...


class GroqClient:
    """
    Thin wrapper around the Groq API (openai/gpt-oss-20b), per PRD §18.
    Requires GROQ_API_KEY in the environment.

    NOTE: not exercised in this sandbox — there's no network path to Groq
    here, and the `groq` package isn't installed. Install it (`pip install
    groq`), set GROQ_API_KEY, and smoke-test this class for real before
    demo day. Everything else in this module is tested against the fake
    client at the bottom of the file.
    """

    def __init__(self, model: str = "openai/gpt-oss-20b", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        from groq import Groq  # imported here so this module loads without the package installed

        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Prompting
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a structured-data extractor for a resume-screening tool.
Extract ONLY information explicitly present in the job description. Do not
infer, guess, or add skills/requirements that are not stated or strongly
implied by the text. Return a single JSON object matching this shape exactly:

{
  "job_title": string,
  "required_skills": [string, ...],
  "preferred_skills": [string, ...],
  "experience_requirements": string or null,
  "min_years_experience": number or null,
  "education_requirements": string or null,
  "responsibilities": [string, ...],
  "other_requirements": [string, ...]
}

Rules:
- required_skills vs preferred_skills must reflect how the JD itself labels
  them (e.g. "must have"/"required" -> required; "nice to have"/"bonus" ->
  preferred). If the JD doesn't distinguish, treat explicitly listed core
  skills as required.
- Do not include protected/sensitive attributes (age, gender, nationality,
  religion, disability, etc.) even if mentioned in the JD.
- Output ONLY the JSON object. No markdown, no commentary.
"""


def _build_user_prompt(jd_text: str) -> str:
    return f"Job description:\n\n{jd_text.strip()}"


# ---------------------------------------------------------------------------
# Rule-based fallback (used if the LLM is unavailable or returns garbage)
# ---------------------------------------------------------------------------

_SECTION_HEADERS = {
    "required": ["requirements", "required skills", "must have", "minimum qualifications"],
    "preferred": ["preferred", "nice to have", "bonus", "preferred qualifications"],
    "responsibilities": ["responsibilities", "what you'll do", "duties", "role"],
}


def _fallback_extract(jd_text: str, job_title_hint: str = "Unknown Role") -> dict:
    """
    Minimal heading + bullet-point heuristic extractor. Deliberately
    conservative — a degraded-mode safety net (PRD §22), not a replacement
    for the LLM path. Catches common resume/JD formatting; won't handle
    prose-style JDs without bullets.
    """
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    buckets: dict[str, list[str]] = {"required": [], "preferred": [], "responsibilities": []}
    current: Optional[str] = None

    for line in lines:
        lower = line.lower().strip(":")
        matched_header = next(
            (bucket for bucket, headers in _SECTION_HEADERS.items() if lower in headers),
            None,
        )
        if matched_header:
            current = matched_header
            continue
        if current and re.match(r"^[\-\*\u2022]\s*", line):
            buckets[current].append(re.sub(r"^[\-\*\u2022]\s*", "", line).strip())

    return {
        "job_title": job_title_hint,
        "required_skills": buckets["required"],
        "preferred_skills": buckets["preferred"],
        "experience_requirements": None,
        "min_years_experience": None,
        "education_requirements": None,
        "responsibilities": buckets["responsibilities"],
        "other_requirements": [],
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def extract_job_profile(
    jd_text: str,
    source_document: str,
    llm_client: Optional[LLMClient] = None,
) -> JobProfile:
    """
    Extract a JobProfile from raw job-description text.

    Tries the LLM path first (if a client is given); falls back to the
    rule-based heuristic extractor on any failure — malformed JSON, missing
    fields, client/network error, or no client provided at all — so a Groq
    outage degrades JD extraction instead of failing it outright (PRD §22).
    """
    raw: Optional[dict] = None

    if llm_client is not None:
        try:
            response_text = llm_client.complete_json(_SYSTEM_PROMPT, _build_user_prompt(jd_text))
            raw = json.loads(response_text)
        except Exception:
            raw = None  # fall through to rule-based extraction

    if raw is None:
        raw = _fallback_extract(jd_text)

    required_skills = normalize_skill_list(raw.get("required_skills", []))
    preferred_skills = normalize_skill_list(raw.get("preferred_skills", []))

    return JobProfile(
        job_title=raw.get("job_title") or "Unknown Role",
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_requirements=raw.get("experience_requirements"),
        min_years_experience=raw.get("min_years_experience"),
        education_requirements=raw.get("education_requirements"),
        responsibilities=raw.get("responsibilities", []),
        other_requirements=raw.get("other_requirements", []),
        source_document=source_document,
    )


# ---------------------------------------------------------------------------
# Smoke test with a fake LLM client — no real Groq call (no network path to
# Groq in this sandbox, and no API key). Swap in GroqClient() once you have
# GROQ_API_KEY set and the groq package installed.
# ---------------------------------------------------------------------------

class _FakeLLMClient:
    """Stands in for GroqClient for offline testing."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps({
            "job_title": "Backend Engineer",
            "required_skills": ["Python", "PostgreSQL", "REST APIs"],
            "preferred_skills": ["AWS", "Docker"],
            "experience_requirements": "3+ years backend development",
            "min_years_experience": 3,
            "education_requirements": "Bachelor's in Computer Science or equivalent experience",
            "responsibilities": ["Design and build REST APIs", "Own database schema design"],
            "other_requirements": [],
        })


_SAMPLE_JD = """
Backend Engineer

Requirements:
- Python
- PostgreSQL
- REST APIs

Preferred:
- AWS
- Docker

Responsibilities:
- Design and build REST APIs
- Own database schema design
"""

if __name__ == "__main__":
    print("=== LLM path (faked client) ===")
    profile_llm = extract_job_profile(_SAMPLE_JD, "jd_sample.txt", llm_client=_FakeLLMClient())
    print(profile_llm.model_dump_json(indent=2))
    assert profile_llm.job_title == "Backend Engineer"
    assert any(s.normalized_name == "PostgreSQL" for s in profile_llm.required_skills)

    print("\n=== Fallback path (no LLM client) ===")
    profile_fallback = extract_job_profile(_SAMPLE_JD, "jd_sample.txt", llm_client=None)
    print(profile_fallback.model_dump_json(indent=2))
    assert any(s.normalized_name == "PostgreSQL" for s in profile_fallback.required_skills)

    print("\nAll smoke tests passed.")
