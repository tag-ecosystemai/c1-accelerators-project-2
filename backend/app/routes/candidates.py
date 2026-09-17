"""HTTP endpoints for candidate processing and comparison."""

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    HTTPException,
    UploadFile,
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
from ..models.user import User
from ..schemas.candidate import (
    CandidateComparisonRequest,
    CandidateComparisonResponse,
    CandidateListResponse,
    CandidateResponse,
    CandidateResultResponse,
    RequiredSkillCoverage,
)
from ..services.candidates import process_resume
from matching.pipeline import MatchingPipeline


router = APIRouter(
    prefix="/jobs",
    tags=["Candidates"],
)


SUPPORTED_RESUME_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def _candidate_response(
    candidate: Candidate,
) -> CandidateResponse:
    return CandidateResponse(
        id=candidate.id,
        job_id=candidate.job_id,
        source_filename=candidate.source_filename,
        profile=candidate.profile,
        processing_status=candidate.processing_status,
        error=candidate.error,
        created_at=candidate.created_at,
    )


def _required_skill_coverage(
    match_result: dict[str, object],
) -> RequiredSkillCoverage | None:
    raw_matches = match_result.get(
        "skill_matches"
    )

    if not isinstance(raw_matches, list):
        return None

    required_matches = [
        match
        for match in raw_matches
        if (
            isinstance(match, dict)
            and isinstance(match.get("skill"), dict)
            and match["skill"].get("required") is True
        )
    ]

    if not required_matches:
        return RequiredSkillCoverage(
            matched=0,
            total=0,
            percentage=0.0,
        )

    matched = sum(
        1
        for match in required_matches
        if match.get("status") == "matched"
    )

    total = len(required_matches)

    return RequiredSkillCoverage(
        matched=matched,
        total=total,
        percentage=(matched / total) * 100,
    )


def _overall_score(
    score_breakdown: dict[str, object],
) -> float | None:
    total = score_breakdown.get("total")

    if isinstance(total, (int, float)):
        return float(total)

    return None


def _result_response(
    candidate: Candidate,
    candidate_result: CandidateResult | None,
    rank: int | None = None,
) -> CandidateResultResponse:
    match_result = (
        candidate_result.match_result
        if candidate_result is not None
        else {}
    )

    score_breakdown = (
        candidate_result.score_breakdown
        if candidate_result is not None
        else {}
    )

    return CandidateResultResponse(
        candidate=_candidate_response(candidate),
        rank=rank,
        overall_score=_overall_score(
            score_breakdown
        ),
        required_skill_coverage=(
            _required_skill_coverage(
                match_result
            )
        ),
        match_result=match_result,
        score_breakdown=score_breakdown,
    )


def _rank_results(
    results: list[CandidateResultResponse],
) -> list[CandidateResultResponse]:
    scored = [
        result
        for result in results
        if result.overall_score is not None
    ]

    unscored = [
        result
        for result in results
        if result.overall_score is None
    ]

    scored.sort(
        key=lambda result: result.overall_score or 0.0,
        reverse=True,
    )

    ranked: list[CandidateResultResponse] = []

    for position, result in enumerate(
        scored,
        start=1,
    ):
        result.rank = position
        ranked.append(result)

    for result in unscored:
        result.rank = None
        ranked.append(result)

    return ranked


def _get_accessible_job(
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


def _get_candidate_result(
    db: Session,
    candidate_id: int,
    job_id: int,
) -> CandidateResult | None:
    return (
        db.query(CandidateResult)
        .filter(
            CandidateResult.candidate_id == candidate_id,
            CandidateResult.job_id == job_id,
        )
        .first()
    )


@router.post(
    "/{job_id}/resumes",
    response_model=CandidateListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resumes(
    job_id: int,
    resumes: list[UploadFile] = File(
        ...,
        description="One or more resume files in PDF, DOCX, or TXT format.",
    ),
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> CandidateListResponse:
    _get_accessible_job(
        db,
        job_id,
        current_user,
        anonymous_token,
    )

    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one resume is required.",
        )

    results: list[CandidateResultResponse] = []

    pipeline = MatchingPipeline()

    for resume in resumes:
        filename = resume.filename or "resume"
        extension = ""

        if "." in filename:
            extension = (
                "." + filename.rsplit(".", 1)[1].lower()
            )

        if extension not in SUPPORTED_RESUME_EXTENSIONS:
            candidate = Candidate(
                job_id=job_id,
                source_filename=filename,
                raw_text="",
                profile={},
                processing_status="failed",
                error=(
                    "Unsupported file type. "
                    "Supported formats: PDF, DOCX, TXT."
                ),
            )

            db.add(candidate)
            db.commit()
            db.refresh(candidate)

            results.append(
                _result_response(
                    candidate,
                    None,
                )
            )

            continue

        content = await resume.read()

        candidate = process_resume(
            db=db,
            job_id=job_id,
            filename=filename,
            file_content=content,
            pipeline=pipeline,
        )

        candidate_result = _get_candidate_result(
            db,
            candidate.id,
            job_id,
        )

        results.append(
            _result_response(
                candidate,
                candidate_result,
            )
        )

    return CandidateListResponse(
        candidates=_rank_results(results)
    )


@router.get(
    "/{job_id}/candidates",
    response_model=CandidateListResponse,
)
def get_candidates(
    job_id: int,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> CandidateListResponse:
    _get_accessible_job(
        db,
        job_id,
        current_user,
        anonymous_token,
    )

    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.job_id == job_id
        )
        .all()
    )

    results: list[CandidateResultResponse] = []

    for candidate in candidates:
        candidate_result = _get_candidate_result(
            db,
            candidate.id,
            job_id,
        )

        results.append(
            _result_response(
                candidate,
                candidate_result,
            )
        )

    return CandidateListResponse(
        candidates=_rank_results(results)
    )


@router.get(
    "/{job_id}/candidates/{candidate_id}",
    response_model=CandidateResultResponse,
)
def get_candidate(
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
) -> CandidateResultResponse:
    _get_accessible_job(
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

    candidate_result = _get_candidate_result(
        db,
        candidate.id,
        job_id,
    )

    return _result_response(
        candidate,
        candidate_result,
    )


@router.post(
    "/{job_id}/candidates/compare",
    response_model=CandidateComparisonResponse,
)
def compare_candidates(
    job_id: int,
    payload: CandidateComparisonRequest,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> CandidateComparisonResponse:
    _get_accessible_job(
        db,
        job_id,
        current_user,
        anonymous_token,
    )

    candidates = (
        db.query(Candidate)
        .filter(
            Candidate.job_id == job_id,
            Candidate.id.in_(payload.candidate_ids),
        )
        .all()
    )

    candidates_by_id = {
        candidate.id: candidate
        for candidate in candidates
    }

    missing_candidate_ids = [
        candidate_id
        for candidate_id in payload.candidate_ids
        if candidate_id not in candidates_by_id
    ]

    if missing_candidate_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more candidates were not found.",
        )

    results: list[CandidateResultResponse] = []

    for candidate_id in payload.candidate_ids:
        candidate = candidates_by_id[candidate_id]

        candidate_result = _get_candidate_result(
            db,
            candidate.id,
            job_id,
        )

        results.append(
            _result_response(
                candidate,
                candidate_result,
            )
        )

    return CandidateComparisonResponse(
        candidates=_rank_results(results)
    )