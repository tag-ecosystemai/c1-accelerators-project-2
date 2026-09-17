from typing import Literal

from pydantic import BaseModel, Field

from intelligence.models import Evidence, Skill


SkillMatchStatus = Literal["matched", "partial", "missing"]


class SkillMatch(BaseModel):
    """Result of matching one job skill against a candidate."""

    skill: Skill
    candidate_skill: Skill | None = None
    status: SkillMatchStatus
    match_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Similarity score for this skill match.",
    )
    evidence: list[Evidence] = Field(default_factory=list)

class MatchResult(BaseModel):
    """Complete matching result for one candidate against a job."""

    candidate_id: str
    skill_matches: list[SkillMatch] = Field(default_factory=list)
    skill_gaps: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)