import pytest
from unittest.mock import Mock

from intelligence.models import CandidateProfile, Evidence, JobProfile, Skill
from matching.matcher import PARTIAL_THRESHOLD, SkillMatcher


def make_skill(
    name: str,
    *,
    required: bool = True,
    evidence_text: str | None = None,
) -> Skill:
    evidence = []

    if evidence_text:
        evidence.append(Evidence(text=evidence_text))

    return Skill(
        name=name,
        normalized_name=name.lower(),
        required=required,
        evidence=evidence,
    )


def make_job(*skills: Skill) -> JobProfile:
    return JobProfile(
        title="Backend Engineer",
        required_skills=list(skills),
    )


def make_candidate(*skills: Skill) -> CandidateProfile:
    return CandidateProfile(
        name="Test Candidate",
        skills=list(skills),
    )


def test_exact_skill_match_returns_matched() -> None:
    matcher = SkillMatcher()

    job = make_job(make_skill("Python"))
    candidate = make_candidate(
        make_skill("Python", evidence_text="Built APIs using Python.")
    )

    result = matcher.match(job, candidate)

    skill_match = result.skill_matches[0]

    assert skill_match.status == "matched"
    assert skill_match.match_score == 1.0
    assert skill_match.candidate_skill is not None
    assert skill_match.candidate_skill.name == "Python"
    assert skill_match.evidence[0].text == "Built APIs using Python."


def test_normalized_skill_match_returns_matched() -> None:
    matcher = SkillMatcher()

    job = make_job(make_skill("PostgreSQL"))
    candidate = make_candidate(make_skill("postgres"))

    result = matcher.match(job, candidate)

    skill_match = result.skill_matches[0]

    assert skill_match.status == "matched"
    assert skill_match.match_score == 1.0


def test_high_semantic_similarity_returns_partial() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [0.95, (1 - 0.95**2) ** 0.5],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("FastAPI"))
    candidate = make_candidate(make_skill("Python API framework"))

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status == "partial"

def test_moderate_semantic_similarity_returns_partial() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [PARTIAL_THRESHOLD, (1 - PARTIAL_THRESHOLD**2) ** 0.5],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("FastAPI"))
    candidate = make_candidate(make_skill("Flask"))

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status == "partial"


def test_low_semantic_similarity_returns_missing() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [0.1, (1 - 0.1**2) ** 0.5],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("FastAPI"))
    candidate = make_candidate(make_skill("Photoshop"))

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status == "missing"
    assert "FastAPI" in result.skill_gaps


def test_missing_skill_is_added_to_skill_gaps() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [0.1, (1 - 0.1**2) ** 0.5],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = make_candidate(make_skill("JavaScript"))

    result = matcher.match(job, candidate)

    assert result.skill_gaps == ["Python"]
    
def test_selects_highest_similarity_candidate_skill() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],  # job skill
        [0.8, 0.6],  # candidate skill 1
        [0.99, 0.1],  # candidate skill 2 — higher similarity
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = make_candidate(
        make_skill("Backend Development"),
        make_skill("Python Programming"),
    )

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].candidate_skill is not None
    assert result.skill_matches[0].candidate_skill.name == "Python Programming"
    assert result.skill_matches[0].match_score == pytest.approx(0.9949371890)


def test_candidate_with_no_skills_results_in_missing() -> None:
    embedding_model = Mock()

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = CandidateProfile(name="Test Candidate")

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status == "missing"
    assert result.skill_matches[0].match_score == 0.0
    assert result.skill_gaps == ["Python"]

    embedding_model.encode.assert_not_called()

def test_similarity_at_partial_threshold_is_partial() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [PARTIAL_THRESHOLD, (1 - PARTIAL_THRESHOLD**2) ** 0.5],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = make_candidate(make_skill("Backend Development"))

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status == "partial"
    assert result.skill_matches[0].match_score == PARTIAL_THRESHOLD


def test_selected_candidate_skill_evidence_is_preserved() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [0.95, 0.3122498999],
    ]

    candidate_skill = make_skill(
        "Python Programming",
        evidence_text="Built backend services using Python.",
    )

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = make_candidate(candidate_skill)

    result = matcher.match(job, candidate)

    assert len(result.skill_matches[0].evidence) == 1
    assert (
        result.skill_matches[0].evidence[0].text
        == "Built backend services using Python."
    )
    
def test_semantically_related_but_different_skill_is_not_matched() -> None:
    embedding_model = Mock()

    embedding_model.encode.side_effect = [
        [1.0, 0.0],
        [0.95, 0.3122498999],
    ]

    matcher = SkillMatcher(embedding_model=embedding_model)

    job = make_job(make_skill("Python"))
    candidate = make_candidate(make_skill("JavaScript"))

    result = matcher.match(job, candidate)

    assert result.skill_matches[0].status != "matched"