from intelligence.models import CandidateProfile, JobProfile, Skill
from intelligence.normalizer import normalize_skill

from matching.embeddings import EmbeddingModel
from matching.models import MatchResult, SkillMatch
from matching.similarity import cosine_similarity


PARTIAL_THRESHOLD = 0.60


class SkillMatcher:
    """Match job skills against candidate skills."""

    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel()

    def match(
        self,
        job: JobProfile,
        candidate: CandidateProfile,
    ) -> MatchResult:
        """Match all job skills against the candidate's skills."""

        skill_matches: list[SkillMatch] = []
        skill_gaps: list[str] = []

        for job_skill in self._job_skills(job):
            skill_match = self._match_skill(
                job_skill,
                candidate.skills,
            )

            skill_matches.append(skill_match)

            if skill_match.status == "missing":
                skill_gaps.append(job_skill.name)

        return MatchResult(
            candidate_id=candidate.name or "unknown",
            skill_matches=skill_matches,
            skill_gaps=skill_gaps,
        )

    @staticmethod
    def _job_skills(job: JobProfile) -> list[Skill]:
        """Return required and preferred skills for matching."""

        return job.required_skills + job.preferred_skills

    def _match_skill(
        self,
        job_skill: Skill,
        candidate_skills: list[Skill],
    ) -> SkillMatch:
        """Match one job skill against all candidate skills."""
        
        if not candidate_skills:
            return SkillMatch(
                skill=job_skill,
                candidate_skill=None,
                status="missing",
                match_score=0.0,
                evidence=[],
            )

        normalized_job_skill = normalize_skill(job_skill.name)

        # Exact/normalized matching takes precedence over semantic matching.
        for candidate_skill in candidate_skills:
            normalized_candidate_skill = normalize_skill(candidate_skill.name)

            if normalized_job_skill == normalized_candidate_skill:
                return SkillMatch(
                    skill=job_skill,
                    candidate_skill=candidate_skill,
                    status="matched",
                    match_score=1.0,
                    evidence=candidate_skill.evidence,
                )

        # No exact match: use semantic similarity.
        best_candidate_skill: Skill | None = None
        best_score = 0.0

        job_embedding = self.embedding_model.encode(job_skill.name)

        for candidate_skill in candidate_skills:
            candidate_embedding = self.embedding_model.encode(
                candidate_skill.name
            )

            score = cosine_similarity(
                job_embedding,
                candidate_embedding,
            )

            if score > best_score:
                best_score = score
                best_candidate_skill = candidate_skill

        if best_score >= PARTIAL_THRESHOLD:
            status = "partial"
        else:
            status = "missing"

        evidence = (
            best_candidate_skill.evidence
            if best_candidate_skill is not None
            else []
        )

        return SkillMatch(
            skill=job_skill,
            candidate_skill=best_candidate_skill,
            status=status,
            match_score=best_score,
            evidence=evidence,
        )