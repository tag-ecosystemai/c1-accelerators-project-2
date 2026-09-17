from scoring.scorer import ScoreBreakdown


def rank_candidates(
    candidates: list[tuple[str, ScoreBreakdown]],
) -> list[tuple[str, ScoreBreakdown]]:
    """Rank candidates from highest total score to lowest."""

    return sorted(
        candidates,
        key=lambda candidate: candidate[1].total,
        reverse=True,
    )