"""Canonical structured models shared by extraction, matching, and the backend."""

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Source text that supports an extracted requirement or skill."""

    source: str = Field(description="The source document identifier.")
    snippet: str = Field(description="The supporting source text.")
    section: str | None = Field(default=None, description="The document section when available.")
    page_number: int | None = Field(default=None, ge=1, description="The page number when available.")


class Skill(BaseModel):
    """A normalized skill with requirement status and evidence."""

    name: str = Field(min_length=1, description="The skill name as extracted.")
    normalized_name: str = Field(min_length=1, description="The canonical normalized skill name.")
    required: bool = Field(description="Whether the skill is required for the role.")
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence supporting this skill.")


class JobProfile(BaseModel):
    """Canonical structured representation of a job description."""

    title: str | None = Field(default=None, description="The job title when available.")
    required_skills: list[Skill] = Field(default_factory=list)
    preferred_skills: list[Skill] = Field(default_factory=list)
    minimum_experience_years: float | None = Field(default=None, ge=0)
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list, description="General profile evidence.")
