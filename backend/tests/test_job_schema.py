import pytest
from pydantic import ValidationError

from backend.app.schemas.job import JobDescriptionInput, JobProfile


def test_job_description_input_accepts_valid_text():
    job_description = JobDescriptionInput(
        text="Python Backend Engineer",
    )

    assert job_description.text == "Python Backend Engineer"


def test_job_description_input_rejects_empty_text():
    with pytest.raises(ValidationError):
        JobDescriptionInput(text="")


def test_job_profile_initializes_requirement_lists_as_empty():
    job_profile = JobProfile(
        title="Backend Engineer",
        raw_text="We are looking for a Backend Engineer.",
    )

    assert job_profile.required_skills == []
    assert job_profile.preferred_skills == []
    assert job_profile.experience_requirements == []
    assert job_profile.education_requirements == []
    assert job_profile.responsibilities == []
    assert job_profile.other_requirements == []