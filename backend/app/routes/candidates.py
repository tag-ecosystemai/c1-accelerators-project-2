from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.candidate import Candidate
from ..models.candidate_result import CandidateResult
from ..models.job import Job
from ..schemas.candidate import (
    CandidateListResponse,
    CandidateResponse,
    CandidateResultResponse,
)
from ..services.candidates import process_resume


router = APIRouter(
    prefix="/jobs",
    tags=["Candidates"],
)


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


@router.post(
    "/{job_id}/resumes",
    response_model=CandidateListResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resumes(
    job_id: int,
    resumes: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> CandidateListResponse:

    if db.get(Job, job_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one resume is required.",
        )

    results: list[CandidateResultResponse] = []

    for resume in resumes:
        filename = resume.filename or "resume"

        content = await resume.read()

        candidate = process_resume(
            db=db,
            job_id=job_id,
            filename=filename,
            file_content=content,
        )

        candidate_result = (
            db.query(CandidateResult)
            .filter(
                CandidateResult.candidate_id == candidate.id,
                CandidateResult.job_id == job_id,
            )
            .first()
        )

        if candidate_result is None:
            results.append(
                CandidateResultResponse(
                    candidate=_candidate_response(candidate),
                    match_result={},
                    score_breakdown={},
                )
            )
            continue

        results.append(
            CandidateResultResponse(
                candidate=_candidate_response(candidate),
                match_result=candidate_result.match_result,
                score_breakdown=candidate_result.score_breakdown,
            )
        )

    return CandidateListResponse(
        candidates=results,
    )


@router.get(
    "/{job_id}/candidates",
    response_model=CandidateListResponse,
)
def get_candidates(
    job_id: int,
    db: Session = Depends(get_db),
) -> CandidateListResponse:

    if db.get(Job, job_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    candidates = (
        db.query(Candidate)
        .filter(Candidate.job_id == job_id)
        .order_by(Candidate.created_at.desc())
        .all()
    )

    results: list[CandidateResultResponse] = []

    for candidate in candidates:
        candidate_result = (
            db.query(CandidateResult)
            .filter(
                CandidateResult.candidate_id == candidate.id,
                CandidateResult.job_id == job_id,
            )
            .first()
        )

        results.append(
            CandidateResultResponse(
                candidate=_candidate_response(candidate),
                match_result=(
                    candidate_result.match_result
                    if candidate_result
                    else {}
                ),
                score_breakdown=(
                    candidate_result.score_breakdown
                    if candidate_result
                    else {}
                ),
            )
        )

    return CandidateListResponse(
        candidates=results,
    )