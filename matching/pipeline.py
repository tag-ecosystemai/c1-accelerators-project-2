from intelligence.models import CandidateProfile, JobProfile
from matching.matcher import SkillMatcher
from matching.models import MatchResult
from scoring.scorer import ScoreBreakdown, ScoringEngine


class CandidateMatchResult:
    """Combined matching and scoring result for one candidate."""

    def __init__(
        self,
        match_result: MatchResult,
        score_breakdown: ScoreBreakdown,
    ) -> None:
        self.match_result = match_result
        self.score_breakdown = score_breakdown


class MatchingPipeline:
    """Run matching and deterministic scoring for one candidate."""

    def __init__(
        self,
        matcher: SkillMatcher | None = None,
        scorer: ScoringEngine | None = None,
    ) -> None:
        self.matcher = matcher or SkillMatcher()
        self.scorer = scorer or ScoringEngine()

    def run(
        self,
        job: JobProfile,
        candidate: CandidateProfile,
        candidate_id: str | None = None,
    ) -> CandidateMatchResult:
        """Match and score a candidate against a job."""

        match_result = self.matcher.match(
            job,
            candidate,
        )

        if candidate_id is not None:
            match_result.candidate_id = candidate_id

        score_breakdown = self.scorer.score(
            job,
            candidate,
            match_result,
        )

        return CandidateMatchResult(
            match_result=match_result,
            score_breakdown=score_breakdown,
        )