from matching.ranking import rank_candidates
from scoring.scorer import ScoreBreakdown


def make_score(total: float) -> ScoreBreakdown:
    return ScoreBreakdown(
        required_skills=total,
        relevant_experience=total,
        responsibilities_alignment=total,
        education=total,
        preferred_skills=total,
        total=total,
    )


def test_candidates_are_ranked_highest_first() -> None:
    candidates = [
        ("Candidate A", make_score(72.0)),
        ("Candidate B", make_score(91.0)),
        ("Candidate C", make_score(84.0)),
    ]

    result = rank_candidates(candidates)

    assert [candidate_id for candidate_id, _ in result] == [
        "Candidate B",
        "Candidate C",
        "Candidate A",
    ]


def test_ranking_preserves_scores() -> None:
    candidates = [
        ("Candidate A", make_score(75.0)),
        ("Candidate B", make_score(90.0)),
    ]

    result = rank_candidates(candidates)

    assert result[0][1].total == 90.0
    assert result[1][1].total == 75.0


def test_equal_scores_preserve_input_order() -> None:
    candidates = [
        ("Candidate A", make_score(80.0)),
        ("Candidate B", make_score(80.0)),
    ]

    result = rank_candidates(candidates)

    assert [candidate_id for candidate_id, _ in result] == [
        "Candidate A",
        "Candidate B",
    ]