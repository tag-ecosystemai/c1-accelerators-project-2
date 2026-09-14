import pytest
from pydantic import ValidationError

from backend.app.schemas.job import JobDescriptionInput
from intelligence.models import Evidence, JobProfile, Skill


def test_job_description_input_accepts_valid_text():
    assert JobDescriptionInput(text="Python Backend Engineer").text == "Python Backend Engineer"


@pytest.mark.parametrize("text", ["", "   \n\t  "])
def test_job_description_input_rejects_empty_or_whitespace_text(text: str):
    with pytest.raises(ValidationError):
        JobDescriptionInput(text=text)


def test_job_description_input_rejects_text_over_fifty_thousand_characters():
    with pytest.raises(ValidationError):
        JobDescriptionInput(text="a" * 50_001)


def test_canonical_job_profile_preserves_skill_and_evidence_metadata():
    evidence = Evidence(text="Requires Python development experience.", location="requirements")
    skill = Skill(name="Python", normalized_name="python", required=True, evidence=[evidence])
    profile = JobProfile(
        title=None,
        required_skills=[skill],
        preferred_skills=[],
        minimum_experience_years=3.0,
        education_requirements=[],
        responsibilities=[],
        evidence=[evidence],
    )

    assert profile.title is None
    assert profile.required_skills[0].normalized_name == "python"
    assert profile.required_skills[0].evidence[0].text.startswith("Requires Python")
    assert profile.minimum_experience_years == 3.0
