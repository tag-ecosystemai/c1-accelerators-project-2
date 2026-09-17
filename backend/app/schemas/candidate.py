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


class RequiredSkillCoverage(BaseModel):
    matched: int
    total: int
    percentage: float


class CandidateResultResponse(BaseModel):
    candidate: CandidateResponse
    rank: int | None
    overall_score: float | None
    required_skill_coverage: RequiredSkillCoverage | None
    match_result: dict[str, object]
    score_breakdown: dict[str, object]


class CandidateListResponse(BaseModel):
    candidates: list[CandidateResultResponse] = Field(
        default_factory=list
    )


class CandidateComparisonRequest(BaseModel):
    candidate_ids: list[int] = Field(
        min_length=2,
        max_length=3,
    )


class CandidateComparisonResponse(BaseModel):
    candidates: list[CandidateResultResponse]