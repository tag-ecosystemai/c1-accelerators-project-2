"""
TalentMatch AI — Resume / Candidate Extraction Pipeline
Owner: Monday Imeobong (NLP / Information Extraction & Skill Intelligence Engineer)

Parsed resume text -> CandidateProfile (schemas.py). Reuses the LLMClient
protocol and GroqClient from jd_extraction.py — same Groq call pattern,
different prompt and output shape.

Evidence handling (PRD §13): evidence must come from extracted resume
content, not be generated solely by the LLM. So the LLM is only asked for
*claims* (skills, employment, education, projects); evidence snippets are
then located by searching the actual parsed resume text/sections for
support — never taken from the LLM's own wording. A claim with no located
support gets an empty evidence list: an explicit "no evidence found"
rather than a fabricated one (PRD §6.4).

Interface note: ParsedSection / ParsedResumeDocument below are placeholders
for whatever Tomoloju's ingestion/ layer actually returns (PRD: "Parsed
Document -> Sections + Text + Source Locations"). Sync field names with him
before wiring this into the real pipeline — ideally these move to ingestion/
entirely and get imported from there instead of redefined here.

Evidence grounding itself now lives in evidence/grounding.py, not in this
file — evidence/ is a shared top-level module, not private to resume
extraction (see that file's docstring for why).
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.schemas import CandidateProfile, EducationEntry, Employment, Project, Skill
from evidence.grounding import find_evidence
from intelligence.jd_extraction import LLMClient  # reuse the same Groq call protocol (GroqClient also lives there)
from intelligence.normalization import get_canonical_skills, normalize


# ---------------------------------------------------------------------------
# Placeholder input contract — replace with Tomoloju's real parser output
# ---------------------------------------------------------------------------

class ParsedSection(BaseModel):
    heading: Optional[str] = None
    text: str
    page_number: Optional[int] = None


class ParsedResumeDocument(BaseModel):
    source_document: str
    full_text: str
    sections: list[ParsedSection] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Prompting
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a structured-data extractor for a resume-screening tool.
Extract ONLY information explicitly stated in the resume text. Do not infer
or guess. Never extract or infer protected/sensitive attributes (age,
gender, race, nationality, religion, marital status, disability, photos,
etc.) even if present in the text — omit them entirely. Return a single
JSON object matching this shape exactly:

{
  "candidate_name": string or null,
  "skills": [string, ...],
  "employment_history": [
    {"company": string, "title": string, "start_date": string or null,
     "end_date": string or null, "is_current": boolean, "description": string or null}
  ],
  "education": [
    {"institution": string, "degree": string or null,
     "field_of_study": string or null, "graduation_year": integer or null}
  ],
  "projects": [
    {"name": string, "description": string or null, "skills_used": [string, ...]}
  ],
  "responsibilities": [string, ...]
}

Dates should be ISO format (YYYY-MM-DD) where a full date is stated, or
null if not determinable from the text. Output ONLY the JSON object. No
markdown, no commentary.
"""


def _build_user_prompt(resume_text: str) -> str:
    return f"Resume text:\n\n{resume_text.strip()}"


# ---------------------------------------------------------------------------
# Rule-based fallback (used if the LLM is unavailable or returns garbage)
# ---------------------------------------------------------------------------

def _fallback_extract(doc: ParsedResumeDocument) -> dict:
    """
    Minimal known-skills scan. A degraded-mode safety net (PRD §22) — finds
    canonical skills that literally appear in the text, nothing else. Much
    weaker than the LLM path; employment/education/projects are left empty
    rather than guessed at.

    Uses word-boundary matching, not plain substring — a plain `in` check
    false-positived on short names like "Go" matching inside "Lagos".
    """
    text_lower = doc.full_text.lower()
    found_skills = [
        name for name in get_canonical_skills()
        if re.search(r"\b" + re.escape(name.lower()) + r"\b", text_lower)
    ]
    return {
        "candidate_name": None,
        "skills": found_skills,
        "employment_history": [],
        "education": [],
        "projects": [],
        "responsibilities": [],
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def extract_candidate_profile(
    doc: ParsedResumeDocument,
    llm_client: Optional[LLMClient] = None,
) -> CandidateProfile:
    """
    Extract a CandidateProfile from a parsed resume document.

    LLM path first (if a client is given) for the claims (skills,
    employment, education, projects); falls back to a known-skills scan on
    any failure. Either way, evidence is grounded afterward by searching
    the actual parsed text — never taken from the LLM's own phrasing.
    """
    raw: Optional[dict] = None
    parsing_status = "success"

    if llm_client is not None:
        try:
            response_text = llm_client.complete_json(_SYSTEM_PROMPT, _build_user_prompt(doc.full_text))
            raw = json.loads(response_text)
        except Exception:
            raw = None

    if raw is None:
        raw = _fallback_extract(doc)
        parsing_status = "partial"

    skills: list[Skill] = []
    for raw_skill in raw.get("skills", []):
        canonical = normalize(raw_skill)
        skills.append(Skill(
            raw_text=raw_skill,
            normalized_name=canonical,
            evidence=find_evidence(raw_skill, doc, associated_field=canonical),
        ))

    employment_history = [
        Employment(
            company=job.get("company", "Unknown"),
            title=job.get("title", "Unknown"),
            start_date=job.get("start_date"),
            end_date=job.get("end_date"),
            is_current=job.get("is_current", False),
            description=job.get("description"),
            evidence=find_evidence(job.get("company", ""), doc, associated_field="employment_history"),
        )
        for job in raw.get("employment_history", [])
    ]

    education = [
        EducationEntry(
            institution=edu.get("institution", "Unknown"),
            degree=edu.get("degree"),
            field_of_study=edu.get("field_of_study"),
            graduation_year=edu.get("graduation_year"),
            evidence=find_evidence(edu.get("institution", ""), doc, associated_field="education"),
        )
        for edu in raw.get("education", [])
    ]

    projects = [
        Project(
            name=proj.get("name", "Unknown"),
            description=proj.get("description"),
            skills_used=proj.get("skills_used", []),
            evidence=find_evidence(proj.get("name", ""), doc, associated_field="projects"),
        )
        for proj in raw.get("projects", [])
    ]

    return CandidateProfile(
        candidate_id=str(uuid.uuid4()),
        candidate_name=raw.get("candidate_name"),
        skills=skills,
        employment_history=employment_history,
        education=education,
        projects=projects,
        responsibilities=raw.get("responsibilities", []),
        source_document=doc.source_document,
        parsing_status=parsing_status,
    )


# ---------------------------------------------------------------------------
# Smoke test with a fake LLM client — no real Groq call in this sandbox
# ---------------------------------------------------------------------------

class _FakeLLMClient:
    """Stands in for GroqClient for offline testing."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps({
            "candidate_name": "Jane Doe",
            "skills": ["Python", "PostgreSQL", "React.js", "AWS"],
            "employment_history": [{
                "company": "Acme Corp",
                "title": "Backend Engineer",
                "start_date": "2020-01-01",
                "end_date": "2023-06-01",
                "is_current": False,
                "description": "Built REST APIs and owned the PostgreSQL schema.",
            }],
            "education": [{
                "institution": "University of Lagos",
                "degree": "B.Sc.",
                "field_of_study": "Computer Science",
                "graduation_year": 2019,
            }],
            "projects": [],
            "responsibilities": ["Built REST APIs", "Owned the PostgreSQL schema"],
        })


_SAMPLE_DOC = ParsedResumeDocument(
    source_document="jane_doe_resume.pdf",
    full_text=(
        "Skills: Python, PostgreSQL, React.js, AWS\n"
        "Acme Corp \u2014 Backend Engineer (2020-01 to 2023-06)\n"
        "Built REST APIs and owned the PostgreSQL schema.\n"
        "B.Sc. Computer Science, University of Lagos, 2019"
    ),
    sections=[
        ParsedSection(heading="Skills", text="Skills: Python, PostgreSQL, React.js, AWS", page_number=1),
        ParsedSection(
            heading="Experience",
            text="Acme Corp \u2014 Backend Engineer (2020-01 to 2023-06)\nBuilt REST APIs and owned the PostgreSQL schema.",
            page_number=1,
        ),
        ParsedSection(heading="Education", text="B.Sc. Computer Science, University of Lagos, 2019", page_number=2),
    ],
)

if __name__ == "__main__":
    print("=== LLM path (faked client) ===")
    profile_llm = extract_candidate_profile(_SAMPLE_DOC, llm_client=_FakeLLMClient())
    print(profile_llm.model_dump_json(indent=2))
    assert profile_llm.candidate_name == "Jane Doe"
    assert any(s.normalized_name == "PostgreSQL" and s.evidence for s in profile_llm.skills)
    assert profile_llm.employment_history[0].evidence  # company name was found in the Experience section
    assert profile_llm.parsing_status == "success"

    print("\n=== Fallback path (no LLM client) ===")
    profile_fallback = extract_candidate_profile(_SAMPLE_DOC, llm_client=None)
    print(profile_fallback.model_dump_json(indent=2))
    assert any(s.normalized_name == "PostgreSQL" for s in profile_fallback.skills)
    assert not any(s.normalized_name == "Go" for s in profile_fallback.skills)  # regression: "go" inside "Lagos"
    assert profile_fallback.parsing_status == "partial"

    print("\nAll smoke tests passed.")
