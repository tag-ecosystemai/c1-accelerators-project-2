from pydantic import BaseModel, Field

from datetime import datetime

from typing import List


class JobDescriptionResponse(BaseModel):
    id: int = Field(
        description="The saved job description identifier.",
    )
    text: str = Field(
        description="The original job description text.",
    )
    created_at: datetime = Field(
        description="The date and time when the job description was saved.",
    )


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

class JobListResponse(BaseModel):
    jobs: List[JobDescriptionResponse] = Field(
        description="The saved job descriptions.",
    )

class JobProfileResponse(JobProfile):
    id: int = Field(
        description="The saved job profile identifier.",
    )
    job_id: int = Field(
        description="The related job description identifier.",
    )