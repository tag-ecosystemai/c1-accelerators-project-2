import pytest

from intelligence.extractor import (
    extract_candidate_profile,
    extract_job_profile,
    extract_skills,
)


class TestExtractSkills:
    def test_extracts_basic_skills(self):
        text = "Python, FastAPI, Docker, PostgreSQL"

        skills = extract_skills(
            text,
            dedicated_section=True,
        )

        normalized_names = {
            skill.normalized_name
            for skill in skills
        }

        assert normalized_names == {
            "python",
            "fastapi",
            "docker",
            "postgresql",
        }

    def test_normalizes_skill_aliases(self):
        text = "Python, Golang, React.js, Fast API, PostgreSQL"

        skills = extract_skills(
            text,
            dedicated_section=True,
        )

        normalized_names = {
            skill.normalized_name
            for skill in skills
        }

        assert normalized_names == {
            "python",
            "go",
            "react",
            "fastapi",
            "postgresql",
        }

    def test_preserves_multiple_evidence_snippets(self):
        text = (
            "Python developer with backend experience. "
            "Built APIs using Python and FastAPI."
        )

        skills = extract_skills(text)

        python_skill = next(
            skill
            for skill in skills
            if skill.normalized_name == "python"
        )

        assert len(python_skill.evidence) == 2
        assert all(
            evidence.text
            for evidence in python_skill.evidence
        )

    def test_deduplicates_same_skill(self):
        text = (
            "Python developer. "
            "Experienced Python engineer."
        )

        skills = extract_skills(text)

        python_skills = [
            skill
            for skill in skills
            if skill.normalized_name == "python"
        ]

        assert len(python_skills) == 1

    def test_ambiguous_go_requires_dedicated_section(self):
        text = "Go, Python, Docker"

        skills = extract_skills(text)

        assert "go" not in {
            skill.normalized_name
            for skill in skills
        }

        dedicated_skills = extract_skills(
            text,
            dedicated_section=True,
        )

        assert "go" in {
            skill.normalized_name
            for skill in dedicated_skills
        }

    def test_ordinary_go_is_not_detected(self):
        text = "Please go through the documentation before applying."

        skills = extract_skills(text)

        assert "go" not in {
            skill.normalized_name
            for skill in skills
        }

    def test_contextual_go_is_detected(self):
        text = "Programming in Go is required."

        job = extract_job_profile(text)

        assert "go" in {
            skill.normalized_name
            for skill in job.required_skills
        }

    def test_contextual_ai_is_detected(self):
        text = "Experience with AI systems is required."

        job = extract_job_profile(text)

        assert "artificial intelligence" in {
            skill.normalized_name
            for skill in job.required_skills
        }

    def test_ordinary_ai_is_not_detected(self):
        text = "The candidate should review AI before the interview."

        skills = extract_skills(text)

        assert "artificial intelligence" not in {
            skill.normalized_name
            for skill in skills
        }

    def test_rest_api_is_detected(self):
        text = "Experience with REST APIs is required."

        job = extract_job_profile(text)

        assert "rest api" in {
            skill.normalized_name
            for skill in job.required_skills
        }


class TestExtractJobProfile:
    def test_extracts_job_title(self):
        text = """Job Title: Backend Engineer

Requirements
- Python
- FastAPI
- Docker
"""

        job = extract_job_profile(text)

        assert job.title == "Backend Engineer"

    def test_extracts_required_and_preferred_skills(self):
        text = """Backend Engineer

Required Skills
- Python
- FastAPI

Preferred Skills
- Docker
- Kubernetes
"""

        job = extract_job_profile(text)

        required = {
            skill.normalized_name
            for skill in job.required_skills
        }

        preferred = {
            skill.normalized_name
            for skill in job.preferred_skills
        }

        assert required == {
            "python",
            "fastapi",
        }

        assert preferred == {
            "docker",
            "kubernetes",
        }

    def test_required_skill_wins_over_preferred_skill(self):
        text = """Backend Engineer

Required Skills
- Python
- FastAPI

Preferred Skills
- Python
- Docker
"""

        job = extract_job_profile(text)

        required = {
            skill.normalized_name
            for skill in job.required_skills
        }

        preferred = {
            skill.normalized_name
            for skill in job.preferred_skills
        }

        assert "python" in required
        assert "python" not in preferred
        assert "docker" in preferred

    def test_extracts_responsibilities(self):
        text = """Backend Engineer

Responsibilities
- Build REST APIs
- Maintain backend services
- Review code
"""

        job = extract_job_profile(text)

        assert job.responsibilities == [
            "Build REST APIs",
            "Maintain backend services",
            "Review code",
        ]

    def test_extracts_education_requirements(self):
        text = """Backend Engineer

Education
- Bachelor's degree in Computer Science
- Related technical degree
"""

        job = extract_job_profile(text)

        assert job.education_requirements == [
            "Bachelor's degree in Computer Science",
            "Related technical degree",
        ]

    def test_extracts_required_experience(self):
        text = """
Backend Engineer

Requirements
- Python
- FastAPI
- Minimum 3 years of experience
"""

        job = extract_job_profile(text)

        assert job.minimum_experience_years == 3.0

    def test_does_not_treat_preferred_experience_as_minimum(self):
        text = """
Backend Engineer

Requirements
- Python

Preferred Skills
- 3+ years of experience preferred
"""

        job = extract_job_profile(text)

        assert job.minimum_experience_years is None

    def test_extracts_professional_experience_requirement(self):
        text = """
Backend Engineer

Requirements
- 5+ years of professional experience required
"""

        job = extract_job_profile(text)

        assert job.minimum_experience_years == 5.0


class TestExtractCandidateProfile:
    def test_extracts_candidate_contact_information(self):
        text = """John Doe
john@example.com
+234 801 234 5678

Skills
Python
FastAPI
"""

        candidate = extract_candidate_profile(text)

        assert candidate.name == "John Doe"
        assert candidate.email == "john@example.com"
        assert candidate.phone == "+234 801 234 5678"

    def test_extracts_candidate_skills_from_skills_section(self):
        text = """John Doe

Skills
Python
Go
FastAPI
Docker
"""

        candidate = extract_candidate_profile(text)

        skills = {
            skill.normalized_name
            for skill in candidate.skills
        }

        assert skills == {
            "python",
            "go",
            "fastapi",
            "docker",
        }

    def test_candidate_go_is_detected_in_skills_section(self):
        text = """John Doe

Skills
Python
Go
"""

        candidate = extract_candidate_profile(text)

        assert "go" in {
            skill.normalized_name
            for skill in candidate.skills
        }

    def test_candidate_sections_are_extracted(self):
        text = """John Doe

Experience
Backend Engineer at Example Company
Built REST APIs using Python.

Education
B.Sc. Computer Science

Projects
TalentMatch AI

Responsibilities
Develop backend services.
"""

        candidate = extract_candidate_profile(text)

        assert candidate.education == [
            "B.Sc. Computer Science"
        ]

        assert candidate.employment_history == [
            "Backend Engineer at Example Company",
            "Built REST APIs using Python.",
        ]

        assert candidate.projects == [
            "TalentMatch AI"
        ]

        assert candidate.responsibilities == [
            "Develop backend services."
        ]

    def test_extracts_candidate_experience_years(self):
        text = """John Doe

5 years of professional experience

Experience
Backend Engineer
"""

        candidate = extract_candidate_profile(text)

        assert candidate.experience_years == 5.0

    def test_candidate_evidence_contains_section_information(self):
        text = """John Doe

Experience
Built backend services using Python.

Education
B.Sc. Computer Science

Projects
TalentMatch AI
"""

        candidate = extract_candidate_profile(text)

        locations = {
            evidence.location
            for evidence in candidate.evidence
        }

        assert locations == {
            "experience",
            "education",
            "projects",
        }


class TestEdgeCases:
    @pytest.mark.parametrize(
        "text",
        [
            "",
            " ",
            "\n\n",
        ],
    )
    def test_empty_text_produces_empty_job_profile(self, text):
        job = extract_job_profile(text)

        assert job.title is None
        assert job.required_skills == []
        assert job.preferred_skills == []
        assert job.minimum_experience_years is None
        assert job.education_requirements == []
        assert job.responsibilities == []
        assert job.evidence == []

    def test_empty_candidate_text(self):
        candidate = extract_candidate_profile("")

        assert candidate.name is None
        assert candidate.email is None
        assert candidate.phone is None
        assert candidate.skills == []
        assert candidate.experience_years is None
        assert candidate.education == []
        assert candidate.employment_history == []
        assert candidate.projects == []
        assert candidate.responsibilities == []
        assert candidate.evidence == []
