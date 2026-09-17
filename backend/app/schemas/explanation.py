from pydantic import BaseModel, Field


class CandidateExplanationResponse(BaseModel):
    candidate_id: int
    explanation: str
    model: str


class CandidateComparisonExplanationRequest(BaseModel):
    candidate_ids: list[int] = Field(
        min_length=2,
        max_length=3,
    )


class CandidateComparisonExplanationResponse(BaseModel):
    candidate_ids: list[int]
    explanation: str
    model: str