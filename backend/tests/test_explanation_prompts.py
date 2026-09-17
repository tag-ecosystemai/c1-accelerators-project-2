from llm.prompts import (
    build_candidate_explanation_prompt,
    build_comparison_explanation_prompt,
)


def test_candidate_prompt_contains_supplied_data():
    prompt = build_candidate_explanation_prompt(
        job_profile={"title": "Backend Engineer"},
        candidate_profile={"name": "Test Candidate"},
        match_result={"matched_skills": ["Python"]},
        score_breakdown={"required_skills": 40},
    )

    assert "Backend Engineer" in prompt
    assert "Test Candidate" in prompt
    assert "Python" in prompt
    assert "required_skills" in prompt


def test_candidate_prompt_preserves_grounding_rules():
    prompt = build_candidate_explanation_prompt(
        job_profile={},
        candidate_profile={},
        match_result={},
        score_breakdown={},
    )

    assert "MUST NOT" in prompt
    assert "invent candidate experience" in prompt
    assert "missing evidence as proof" in prompt
    assert "Do not make the hiring decision" in prompt


def test_comparison_prompt_contains_candidate_data():
    prompt = build_comparison_explanation_prompt(
        job_profile={"title": "ML Engineer"},
        candidates=[
            {
                "candidate_id": 1,
                "overall_score": 90,
            },
            {
                "candidate_id": 2,
                "overall_score": 80,
            },
        ],
    )

    assert "ML Engineer" in prompt
    assert "candidate_id" in prompt
    assert "90" in prompt
    assert "80" in prompt


def test_comparison_prompt_prevents_ranking_changes():
    prompt = build_comparison_explanation_prompt(
        job_profile={},
        candidates=[],
    )

    assert "Preserve every supplied score and ranking exactly" in prompt
    assert "Do not create a new ranking" in prompt
    assert "declare a winner" in prompt
    assert "recruiter remains responsible" in prompt