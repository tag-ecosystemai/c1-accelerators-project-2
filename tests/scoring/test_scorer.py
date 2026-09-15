from intelligence.models import CandidateProfile, JobProfile, Skill
from unittest.mock import Mock
from matching.models import MatchResult, SkillMatch
from scoring.scorer import (
    EDUCATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    PREFERRED_SKILLS_WEIGHT,
    REQUIRED_SKILLS_WEIGHT,
    RESPONSIBILITIES_WEIGHT,
    ScoringEngine,
)


def make_skill(
    name: str,
    *,
    required: bool = True,
) -> Skill:
    return Skill(
        name=name,
        normalized_name=name.lower(),
        required=required,
    )


def make_match(
    skill: Skill,
    score: float,
) -> SkillMatch:
    status = "matched" if score == 1.0 else (
        "partial" if score >= 0.6 else "missing"
    )

    return SkillMatch(
        skill=skill,
        candidate_skill=None,
        status=status,
        match_score=score,
    )
    
def make_scoring_engine() -> ScoringEngine:
    return ScoringEngine(
        embedding_model=Mock(),
    )


def test_perfect_candidate_scores_100() -> None:
    job = JobProfile(
        title="Backend Engineer",
        required_skills=[make_skill("Python")],
        preferred_skills=[
            make_skill("Docker", required=False),
        ],
        minimum_experience_years=3,
        education_requirements=["Computer Science"],
    )

    candidate = CandidateProfile(
        name="Perfect Candidate",
        experience_years=3,
        education=["BSc Computer Science"],
        responsibilities=["Build backend services"],
    )

    match_result = MatchResult(
        candidate_id="Perfect Candidate",
        skill_matches=[
            make_match(make_skill("Python"), 1.0),
            make_match(make_skill("Docker", required=False), 1.0),
        ],
    )

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.required_skills == 100.0
    assert result.preferred_skills == 100.0
    assert result.relevant_experience == 100.0
    assert result.education == 100.0
    assert result.responsibilities_alignment == 100.0
    assert result.total == 100.0


def test_required_skill_score_uses_match_scores() -> None:
    job = JobProfile(
        required_skills=[
            make_skill("Python"),
            make_skill("FastAPI"),
        ],
    )

    candidate = CandidateProfile(name="Test Candidate")

    match_result = MatchResult(
        candidate_id="Test Candidate",
        skill_matches=[
            make_match(make_skill("Python"), 1.0),
            make_match(make_skill("FastAPI"), 0.5),
        ],
    )

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.required_skills == 75.0


def test_missing_required_skills_reduce_score() -> None:
    job = JobProfile(
        required_skills=[
            make_skill("Python"),
            make_skill("FastAPI"),
        ],
    )

    candidate = CandidateProfile(name="Test Candidate")

    match_result = MatchResult(
        candidate_id="Test Candidate",
        skill_matches=[
            make_match(make_skill("Python"), 1.0),
            make_match(make_skill("FastAPI"), 0.0),
        ],
    )

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.required_skills == 50.0


def test_experience_score_caps_at_100() -> None:
    job = JobProfile(minimum_experience_years=3)
    candidate = CandidateProfile(
        name="Experienced Candidate",
        experience_years=6,
    )

    match_result = MatchResult(candidate_id="Experienced Candidate")

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.relevant_experience == 100.0


def test_insufficient_experience_is_proportional() -> None:
    job = JobProfile(minimum_experience_years=4)
    candidate = CandidateProfile(
        name="Candidate",
        experience_years=2,
    )

    match_result = MatchResult(candidate_id="Candidate")

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.relevant_experience == 50.0


def test_no_experience_requirement_scores_100() -> None:
    job = JobProfile()
    candidate = CandidateProfile(name="Candidate")

    match_result = MatchResult(candidate_id="Candidate")

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.relevant_experience == 100.0


def test_education_requirement_is_matched() -> None:
    job = JobProfile(
        education_requirements=["Computer Science"],
    )

    candidate = CandidateProfile(
        name="Candidate",
        education=["BSc Computer Science"],
    )

    match_result = MatchResult(candidate_id="Candidate")

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.education == 100.0


def test_missing_education_scores_zero() -> None:
    job = JobProfile(
        education_requirements=["Computer Science"],
    )

    candidate = CandidateProfile(
        name="Candidate",
        education=[],
    )

    match_result = MatchResult(candidate_id="Candidate")

    result = ScoringEngine().score(
        job,
        candidate,
        match_result,
    )

    assert result.education == 0.0


def test_weights_sum_to_100_percent() -> None:
    total_weight = (
        REQUIRED_SKILLS_WEIGHT
        + EXPERIENCE_WEIGHT
        + RESPONSIBILITIES_WEIGHT
        + EDUCATION_WEIGHT
        + PREFERRED_SKILLS_WEIGHT
    )

    assert total_weight == 1.0
    
def test_responsibilities_are_semantically_matched() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],  # job responsibility
        [0.9, (1 - 0.9**2) ** 0.5],  # candidate responsibility
    ]

    engine = ScoringEngine(
        embedding_model=embedding_model,
    )

    job = JobProfile(
        responsibilities=["Build backend APIs"],
    )

    candidate = CandidateProfile(
        name="Candidate",
        responsibilities=["Develop backend services"],
    )

    match_result = MatchResult(candidate_id="Candidate")

    result = engine.score(
        job,
        candidate,
        match_result,
    )

    assert result.responsibilities_alignment == 90.0


def test_unrelated_responsibilities_score_zero() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],  # job responsibility
        [0.2, (1 - 0.2**2) ** 0.5],  # candidate responsibility
    ]

    engine = ScoringEngine(
        embedding_model=embedding_model,
    )

    job = JobProfile(
        responsibilities=["Build backend APIs"],
    )

    candidate = CandidateProfile(
        name="Candidate",
        responsibilities=["Design marketing campaigns"],
    )

    match_result = MatchResult(candidate_id="Candidate")

    result = engine.score(
        job,
        candidate,
        match_result,
    )

    assert result.responsibilities_alignment == 0.0