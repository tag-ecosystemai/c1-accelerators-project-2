"""API schemas for job descriptions and canonical job profiles."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from intelligence.models import JobProfile


class JobDescriptionInput(BaseModel):
    """Input used to create a job description."""

    text: str = Field(
        min_length=1,
        max_length=50_000,
        description="The job description text.",
    )

    @field_validator("text")
    @classmethod
    def text_must_contain_non_whitespace_characters(cls, value: str) -> str:
        """Reject text that contains only whitespace."""
        if not value.strip():
            raise ValueError("The job description text cannot be blank.")
        return value


class JobDescriptionResponse(BaseModel):
    """A persisted job description."""

    id: int = Field(description="The saved job description identifier.")
    text: str = Field(description="The original job description text.")
    created_at: datetime = Field(description="When the job description was saved.")


class JobListResponse(BaseModel):
    """A collection of persisted job descriptions."""

    jobs: list[JobDescriptionResponse] = Field(description="The saved job descriptions.")


class JobProfileResponse(JobProfile):
    """A canonical job profile linked to its persisted job description."""

    id: int = Field(description="The saved job profile identifier.")
    job_id: int = Field(description="The related job description identifier.")
