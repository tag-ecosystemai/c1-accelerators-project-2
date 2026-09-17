"""API schemas for job descriptions and canonical job profiles."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from intelligence.models import JobProfile


class JobDescriptionInput(BaseModel):
    """Input used to create a job description."""

    text: str = Field(
        min_length=1,
        max_length=50_000,
    )

    @field_validator("text")
    @classmethod
    def text_must_contain_non_whitespace_characters(
        cls,
        value: str,
    ) -> str:
        if not value.strip():
            raise ValueError(
                "The job description text cannot be blank."
            )

        return value


class JobDescriptionResponse(BaseModel):
    id: int
    text: str
    created_at: datetime


class JobListResponse(BaseModel):
    jobs: list[JobDescriptionResponse] = Field(
        default_factory=list
    )


class JobProfileResponse(JobProfile):
    id: int
    job_id: int


class JobCreatedResponse(BaseModel):
    job: JobDescriptionResponse
    profile: JobProfileResponse