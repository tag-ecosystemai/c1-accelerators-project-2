import os
import tempfile
from pathlib import Path

from sqlalchemy.orm import Session

from intelligence.extractor import extract_candidate_profile
from intelligence.models import JobProfile

from matching.pipeline import MatchingPipeline

from ..models.candidate import Candidate
from ..models.candidate_result import CandidateResult
from ..models.job import Job
from ..models.job_profile import JobProfile as JobProfileModel


def _load_job_profile(
    db: Session,
    job_id: int,
) -> JobProfile:
    profile = (
        db.query(JobProfileModel)
        .filter(JobProfileModel.job_id == job_id)
        .first()
    )

    if profile is None:
        raise ValueError("Job profile not found.")

    return JobProfile.model_validate(
        {
            "title": profile.title,
            "required_skills": profile.required_skills,
            "preferred_skills": profile.preferred_skills,
            "minimum_experience_years": (
                profile.minimum_experience_years
            ),
            "education_requirements": (
                profile.education_requirements
            ),
            "responsibilities": profile.responsibilities,
            "evidence": profile.evidence,
        }
    )


def process_resume(
    db: Session,
    job_id: int,
    filename: str,
    file_content: bytes,
) -> Candidate:
    """Parse, extract, match, score, and persist one resume."""

    if db.get(Job, job_id) is None:
        raise ValueError("Job description not found.")

    job_profile = _load_job_profile(db, job_id)

    suffix = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temporary_file:
        temporary_file.write(file_content)
        temporary_path = temporary_file.name

    try:
        from backend.app.ingestion.dispatcher import parse_resume

        parsed_document = parse_resume(temporary_path)
    finally:
        os.unlink(temporary_path)

    candidate = Candidate(
        job_id=job_id,
        source_filename=filename,
        raw_text=parsed_document.raw_text,
        profile={},
        processing_status="processing",
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    if parsed_document.parse_status == "failed":
        candidate.processing_status = "failed"
        candidate.error = parsed_document.error
        db.commit()
        db.refresh(candidate)
        return candidate

    try:
        candidate_profile = extract_candidate_profile(
            parsed_document.raw_text,
        )

        candidate.profile = candidate_profile.model_dump(
            mode="json",
        )

        pipeline = MatchingPipeline()

        result = pipeline.run(
            job_profile,
            candidate_profile,
        )

        candidate_result = CandidateResult(
            candidate_id=candidate.id,
            job_id=job_id,
            match_result=result.match_result.model_dump(
                mode="json",
            ),
            score_breakdown=result.score_breakdown.model_dump(
                mode="json",
            ),
        )

        db.add(candidate_result)

        candidate.processing_status = "completed"
        candidate.error = None

        db.commit()
        db.refresh(candidate)

        return candidate

    except Exception as exc:
        candidate.processing_status = "failed"
        candidate.error = str(exc)

        db.commit()
        db.refresh(candidate)

        return candidate