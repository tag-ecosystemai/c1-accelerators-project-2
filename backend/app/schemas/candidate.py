from datetime import datetime

from pydantic import BaseModel, Field


class CandidateResponse(BaseModel):
    id: int
    job_id: int
    source_filename: str
    profile: dict[str, object]
    processing_status: str
    error: str | None
    created_at: datetime


class CandidateResultResponse(BaseModel):
    candidate: CandidateResponse
    match_result: dict[str, object]
    score_breakdown: dict[str, object]


class CandidateListResponse(BaseModel):
    candidates: list[CandidateResultResponse] = Field(
        default_factory=list,
    )