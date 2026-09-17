from pydantic import BaseModel, Field

from intelligence.models import CandidateProfile, JobProfile
from matching.embeddings import EmbeddingModel
from matching.models import MatchResult
from matching.similarity import cosine_similarity


REQUIRED_SKILLS_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.25
RESPONSIBILITIES_WEIGHT = 0.15
EDUCATION_WEIGHT = 0.10
PREFERRED_SKILLS_WEIGHT = 0.10

RESPONSIBILITY_MATCH_THRESHOLD = 0.60


class ScoreBreakdown(BaseModel):
    """Deterministic candidate score breakdown."""

    required_skills: float = Field(ge=0.0, le=100.0)
    relevant_experience: float = Field(ge=0.0, le=100.0)
    responsibilities_alignment: float = Field(ge=0.0, le=100.0)
    education: float = Field(ge=0.0, le=100.0)
    preferred_skills: float = Field(ge=0.0, le=100.0)
    total: float = Field(ge=0.0, le=100.0)


class ScoringEngine:
    """Calculate deterministic candidate fit scores."""

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel()

    def score(
        self,
        job: JobProfile,
        candidate: CandidateProfile,
        match_result: MatchResult,
    ) -> ScoreBreakdown:
        """Calculate the weighted candidate score."""

        required_skills = self._required_skill_score(match_result)
        preferred_skills = self._preferred_skill_score(match_result)

        relevant_experience = self._experience_score(
            job,
            candidate,
        )

        responsibilities_alignment = self._responsibilities_score(
            job,
            candidate,
        )

        education = self._education_score(
            job,
            candidate,
        )

        total = (
            required_skills * REQUIRED_SKILLS_WEIGHT
            + relevant_experience * EXPERIENCE_WEIGHT
            + responsibilities_alignment * RESPONSIBILITIES_WEIGHT
            + education * EDUCATION_WEIGHT
            + preferred_skills * PREFERRED_SKILLS_WEIGHT
        )

        return ScoreBreakdown(
            required_skills=required_skills,
            relevant_experience=relevant_experience,
            responsibilities_alignment=responsibilities_alignment,
            education=education,
            preferred_skills=preferred_skills,
            total=total,
        )

    @staticmethod
    def _required_skill_score(match_result: MatchResult) -> float:
        """Calculate required-skill coverage as a percentage."""

        required_matches = [
            match
            for match in match_result.skill_matches
            if match.skill.required
        ]

        if not required_matches:
            return 0.0

        matched_score = sum(
            match.match_score
            for match in required_matches
        )

        return (matched_score / len(required_matches)) * 100

    @staticmethod
    def _preferred_skill_score(match_result: MatchResult) -> float:
        """Calculate preferred-skill coverage as a percentage."""

        preferred_matches = [
            match
            for match in match_result.skill_matches
            if not match.skill.required
        ]

        if not preferred_matches:
            return 0.0

        matched_score = sum(
            match.match_score
            for match in preferred_matches
        )

        return (matched_score / len(preferred_matches)) * 100

    @staticmethod
    def _experience_score(
        job: JobProfile,
        candidate: CandidateProfile,
    ) -> float:
        """Calculate relevant experience as a percentage."""

        required_years = job.minimum_experience_years

        if required_years is None:
            return 100.0

        candidate_years = candidate.experience_years or 0.0

        if required_years <= 0:
            return 100.0

        return min(candidate_years / required_years, 1.0) * 100

    def _responsibilities_score(
        self,
        job: JobProfile,
        candidate: CandidateProfile,
    ) -> float:
        """Calculate responsibility alignment using semantic similarity."""

        if not job.responsibilities:
            return 100.0

        if not candidate.responsibilities:
            return 0.0

        candidate_embeddings = [
            self.embedding_model.encode(responsibility)
            for responsibility in candidate.responsibilities
        ]

        scores: list[float] = []

        for job_responsibility in job.responsibilities:
            job_embedding = self.embedding_model.encode(
                job_responsibility
            )

            best_score = 0.0

            for candidate_embedding in candidate_embeddings:
                score = cosine_similarity(
                    job_embedding,
                    candidate_embedding,
                )

                if score > best_score:
                    best_score = score

            if best_score >= RESPONSIBILITY_MATCH_THRESHOLD:
                scores.append(best_score)
            else:
                scores.append(0.0)

        return (sum(scores) / len(scores)) * 100

    @staticmethod
    def _education_score(
        job: JobProfile,
        candidate: CandidateProfile,
    ) -> float:
        """Calculate education requirement coverage."""

        if not job.education_requirements:
            return 100.0

        if not candidate.education:
            return 0.0

        candidate_education = " ".join(
            education.lower()
            for education in candidate.education
        )

        matched = sum(
            1
            for requirement in job.education_requirements
            if requirement.lower() in candidate_education
        )

        return (matched / len(job.education_requirements)) * 100