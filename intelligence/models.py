from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Source text supporting an extracted fact."""

    text: str = Field(min_length=1)
    location: str | None = None


class Skill(BaseModel):
    """A normalized skill extracted from a document."""

    name: str = Field(min_length=1)
    normalized_name: str = Field(min_length=1)
    required: bool = False
    evidence: list[Evidence] = Field(default_factory=list)


class JobProfile(BaseModel):
    """Structured information extracted from a job description."""

    title: str | None = None
    required_skills: list[Skill] = Field(default_factory=list)
    preferred_skills: list[Skill] = Field(default_factory=list)
    minimum_experience_years: float | None = None
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Structured information extracted from a candidate resume."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None

    skills: list[Skill] = Field(default_factory=list)

    experience_years: float | None = None
    education: list[str] = Field(default_factory=list)
    employment_history: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

    evidence: list[Evidence] = Field(default_factory=list)