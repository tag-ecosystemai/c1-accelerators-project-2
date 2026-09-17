from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..core.screening_access import (
    ANONYMOUS_SCREENING_COOKIE,
    get_accessible_job,
    get_optional_current_user,
)
from ..database import get_db
from ..models.candidate import Candidate
from ..models.candidate_result import CandidateResult
from ..models.job import Job
from ..models.job_profile import JobProfile
from ..models.user import User
from ..schemas.explanation import (
    CandidateComparisonExplanationRequest,
    CandidateComparisonExplanationResponse,
    CandidateExplanationResponse,
)
from ..services.explanations import ExplanationService


router = APIRouter(
    prefix="/jobs",
    tags=["Explanations"],
)


def _get_accessible_job_or_404(
    db: Session,
    job_id: int,
    current_user: User | None,
    anonymous_token: str | None,
) -> Job:
    job = get_accessible_job(
        db=db,
        job_id=job_id,
        current_user=current_user,
        anonymous_token=anonymous_token,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    return job


def _get_job_profile(
    db: Session,
    job_id: int,
) -> JobProfile:
    job_profile = (
        db.query(JobProfile)
        .filter(
            JobProfile.job_id == job_id
        )
        .first()
    )

    if job_profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job profile is not available.",
        )

    return job_profile


@router.get(
    "/{job_id}/candidates/{candidate_id}/explanation",
    response_model=CandidateExplanationResponse,
)
def explain_candidate(
    job_id: int,
    candidate_id: int,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> CandidateExplanationResponse:
    _get_accessible_job_or_404(
        db,
        job_id,
        current_user,
        anonymous_token,
    )

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id,
            Candidate.job_id == job_id,
        )
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found.",
        )

    candidate_result = (
        db.query(CandidateResult)
        .filter(
            CandidateResult.candidate_id == candidate_id,
            CandidateResult.job_id == job_id,
        )
        .first()
    )

    if candidate_result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate matching result is not available.",
        )

    job_profile = _get_job_profile(
        db,
        job_id,
    )

    try:
        service = ExplanationService()

        explanation = service.generate_candidate_explanation(
            job_profile={
                "title": job_profile.title,
                "required_skills": job_profile.required_skills,
                "preferred_skills": job_profile.preferred_skills,
                "minimum_experience_years": (
                    job_profile.minimum_experience_years
                ),
                "education_requirements": (
                    job_profile.education_requirements
                ),
                "responsibilities": job_profile.responsibilities,
            },
            candidate_profile=candidate.profile,
            match_result=candidate_result.match_result,
            score_breakdown=candidate_result.score_breakdown,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Explanation service unavailable: {exc}",
        ) from exc

    return CandidateExplanationResponse(
        candidate_id=candidate.id,
        explanation=explanation,
        model=service.model,
    )


@router.post(
    "/{job_id}/candidates/compare/explanation",
    response_model=CandidateComparisonExplanationResponse,
)
def explain_candidate_comparison(
    job_id: int,
    payload: CandidateComparisonExplanationRequest,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> CandidateComparisonExplanationResponse:
    _get_accessible_job_or_404(
        db,
        job_id,
        current_user,
        anonymous_token,
    )

    candidate_ids = payload.candidate_ids

    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.job_id == job_id,
            Candidate.id.in_(candidate_ids),
        )
        .all()
    )

    candidates_by_id = {
        candidate.id: candidate
        for candidate in candidates
    }

    missing_candidate_ids = [
        candidate_id
        for candidate_id in candidate_ids
        if candidate_id not in candidates_by_id
    ]

    if missing_candidate_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more candidates were not found.",
        )

    candidate_results = (
        db.query(CandidateResult)
        .filter(
            CandidateResult.job_id == job_id,
            CandidateResult.candidate_id.in_(candidate_ids),
        )
        .all()
    )

    results_by_candidate_id = {
        result.candidate_id: result
        for result in candidate_results
    }

    missing_result_ids = [
        candidate_id
        for candidate_id in candidate_ids
        if candidate_id not in results_by_candidate_id
    ]

    if missing_result_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "One or more candidates do not have "
                "matching results."
            ),
        )

    job_profile = _get_job_profile(
        db,
        job_id,
    )

    candidates_for_explanation = []

    for candidate_id in candidate_ids:
        candidate = candidates_by_id[candidate_id]
        candidate_result = results_by_candidate_id[candidate_id]

        candidates_for_explanation.append(
            {
                "candidate_id": candidate.id,
                "candidate_profile": candidate.profile,
                "match_result": candidate_result.match_result,
                "score_breakdown": (
                    candidate_result.score_breakdown
                ),
            }
        )

    try:
        service = ExplanationService()

        explanation = service.generate_comparison_explanation(
            job_profile={
                "title": job_profile.title,
                "required_skills": job_profile.required_skills,
                "preferred_skills": job_profile.preferred_skills,
                "minimum_experience_years": (
                    job_profile.minimum_experience_years
                ),
                "education_requirements": (
                    job_profile.education_requirements
                ),
                "responsibilities": job_profile.responsibilities,
            },
            candidates=candidates_for_explanation,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Comparison explanation service unavailable: "
                f"{exc}"
            ),
        ) from exc

    return CandidateComparisonExplanationResponse(
        candidate_ids=candidate_ids,
        explanation=explanation,
        model=service.model,
    )