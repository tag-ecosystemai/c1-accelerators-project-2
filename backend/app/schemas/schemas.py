"""
TalentMatch AI — Extraction Schemas
Owner: Monday Imeobong (NLP / Information Extraction & Skill Intelligence Engineer)

These are the structured outputs produced by the extraction pipeline:
  - JobProfile        <- from job-description extraction
  - CandidateProfile   <- from resume extraction

Both are built from shared building blocks (Skill, Evidence, Employment,
Education, Project) so everything downstream (matching, scoring,
explanation) consumes one consistent shape.

Sync note: Skill / Evidence are contracts shared with Souley's core schema
set. SkillMatch and ScoreBreakdown live in the matching/scoring module
(Iyamokuma's), not here — confirm field names line up before backend
integration.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SkillRequirementLevel(str, Enum):
    """Whether a skill is required or merely preferred for the role."""
    REQUIRED = "required"
    PREFERRED = "preferred"


class MatchConfidence(str, Enum):
    """
    Confidence that a candidate's text supports a given skill. Populated by
    the normalization layer, consumed by the matching engine. Distinguishes
    'no evidence found' from 'proven absent' per PRD §6.4.
    """
    EXACT = "exact"        # exact or normalized string match
    RELATED = "related"    # partial / related skill relationship
    NONE = "none"          # no supporting evidence found


# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------

class Evidence(BaseModel):
    """
    Traceable support for a claim. Must originate from extracted resume/JD
    content — never generated solely by the LLM (PRD §13).
    """
    source_document: str = Field(..., description="Filename or identifier of the source document")
    section: Optional[str] = Field(None, description="Resume/JD section, e.g. 'Experience', 'Skills'")
    page_number: Optional[int] = Field(None, description="Page number, where available")
    text_snippet: str = Field(..., description="Verbatim or near-verbatim supporting text")
    associated_field: Optional[str] = Field(
        None, description="The requirement or skill this evidence supports, e.g. 'Python'"
    )


class Skill(BaseModel):
    """A single skill, before or after normalization."""
    raw_text: str = Field(..., description="Skill as it appeared in the source text")
    normalized_name: str = Field(..., description="Canonical form after normalization, e.g. 'React'")
    requirement_level: Optional[SkillRequirementLevel] = Field(
        None, description="Set on JobProfile skills only; left None for candidate skills"
    )
    confidence: Optional[MatchConfidence] = Field(
        None, description="Set when this Skill represents a candidate's evidence against a JD skill"
    )
    evidence: list[Evidence] = Field(default_factory=list)

    @field_validator("normalized_name")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("normalized_name must not be empty")
        return v.strip()


class Employment(BaseModel):
    company: str
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    evidence: list[Evidence] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    evidence: list[Evidence] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    skills_used: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# JobProfile — output of JD extraction
# ---------------------------------------------------------------------------

class JobProfile(BaseModel):
    job_title: str
    required_skills: list[Skill] = Field(default_factory=list)
    preferred_skills: list[Skill] = Field(default_factory=list)
    experience_requirements: Optional[str] = Field(
        None, description="Free-text summary, e.g. '3+ years backend development'"
    )
    min_years_experience: Optional[float] = None
    education_requirements: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)
    other_requirements: list[str] = Field(default_factory=list)
    source_document: str

    @field_validator("required_skills")
    @classmethod
    def _tag_required(cls, skills: list[Skill]) -> list[Skill]:
        for s in skills:
            s.requirement_level = SkillRequirementLevel.REQUIRED
        return skills

    @field_validator("preferred_skills")
    @classmethod
    def _tag_preferred(cls, skills: list[Skill]) -> list[Skill]:
        for s in skills:
            s.requirement_level = SkillRequirementLevel.PREFERRED
        return skills


# ---------------------------------------------------------------------------
# CandidateProfile — output of resume extraction
# ---------------------------------------------------------------------------

class CandidateProfile(BaseModel):
    candidate_id: str = Field(..., description="Generated identifier — auth/PII handling is out of scope")
    candidate_name: Optional[str] = Field(None, description="Name if present in resume; identifier used otherwise")
    skills: list[Skill] = Field(default_factory=list)
    employment_history: list[Employment] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    source_document: str
    parsing_status: str = Field("success", description="'success' | 'partial' | 'failed' — set by ingestion layer")

    @property
    def total_years_experience(self) -> float:
        """
        Rough total from employment_history date ranges.
        Placeholder — refine once Employment dates are reliably populated.
        """
        total_days = 0
        for job in self.employment_history:
            if job.start_date:
                end = job.end_date or date.today()
                total_days += (end - job.start_date).days
        return round(total_days / 365.25, 1)


if __name__ == "__main__":
    # Smoke test
    jp = JobProfile(
        job_title="Backend Engineer",
        required_skills=[Skill(raw_text="Python", normalized_name="Python")],
        preferred_skills=[Skill(raw_text="AWS", normalized_name="AWS")],
        responsibilities=["Build REST APIs"],
        source_document="jd_sample.txt",
    )
    print(jp.model_dump_json(indent=2))
