from pydantic import BaseModel, Field


class JobDescriptionInput(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=50_000,
        description="The job description text.",
    )


class JobProfile(BaseModel):
    title: str = Field(
        min_length=1,
        description="The job title.",
    )
    raw_text: str = Field(
        min_length=1,
        description="The original job description text.",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills required for the role.",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Skills preferred for the role.",
    )
    experience_requirements: list[str] = Field(
        default_factory=list,
        description="Required experience qualifications.",
    )
    education_requirements: list[str] = Field(
        default_factory=list,
        description="Required education qualifications.",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description="Main role responsibilities.",
    )
    other_requirements: list[str] = Field(
        default_factory=list,
        description="Other explicit job requirements.",
    )