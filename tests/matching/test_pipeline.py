from unittest.mock import Mock

from intelligence.models import CandidateProfile, JobProfile, Skill
from matching.models import MatchResult
from matching.pipeline import CandidateMatchResult, MatchingPipeline
from scoring.scorer import ScoreBreakdown


def test_pipeline_combines_matching_and_scoring() -> None:
    matcher = Mock()
    scorer = Mock()

    match_result = MatchResult(
        candidate_id="Candidate",
    )

    score_breakdown = ScoreBreakdown(
        required_skills=80.0,
        relevant_experience=75.0,
        responsibilities_alignment=90.0,
        education=100.0,
        preferred_skills=50.0,
        total=80.0,
    )

    matcher.match.return_value = match_result
    scorer.score.return_value = score_breakdown

    pipeline = MatchingPipeline(
        matcher=matcher,
        scorer=scorer,
    )

    job = JobProfile(title="Backend Engineer")
    candidate = CandidateProfile(name="Candidate")

    result = pipeline.run(job, candidate)

    assert isinstance(result, CandidateMatchResult)
    assert result.match_result is match_result
    assert result.score_breakdown is score_breakdown

    matcher.match.assert_called_once_with(
        job,
        candidate,
    )

    scorer.score.assert_called_once_with(
        job,
        candidate,
        match_result,
    )


def test_pipeline_preserves_match_result() -> None:
    matcher = Mock()
    scorer = Mock()

    skill = Skill(
        name="Python",
        normalized_name="python",
        required=True,
    )

    match_result = MatchResult(
        candidate_id="Candidate",
        skill_matches=[],
        skill_gaps=["Python"],
    )

    score_breakdown = ScoreBreakdown(
        required_skills=0.0,
        relevant_experience=50.0,
        responsibilities_alignment=100.0,
        education=100.0,
        preferred_skills=0.0,
        total=47.5,
    )

    matcher.match.return_value = match_result
    scorer.score.return_value = score_breakdown

    pipeline = MatchingPipeline(
        matcher=matcher,
        scorer=scorer,
    )

    result = pipeline.run(
        JobProfile(required_skills=[skill]),
        CandidateProfile(name="Candidate"),
    )

    assert result.match_result.skill_gaps == ["Python"]
    assert result.score_breakdown.total == 47.5