"""HTTP endpoints for job descriptions and extracted job profiles."""

import os
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from intelligence.extractor import extract_job_profile

from ..core.auth import get_current_user
from ..core.screening_access import (
    ANONYMOUS_SCREENING_COOKIE,
    create_anonymous_screening_token,
    get_accessible_job,
    get_optional_current_user,
)
from ..database import get_db
from ..ingestion.dispatcher import parse_document
from ..models.job import Job
from ..models.job_profile import JobProfile as JobProfileModel
from ..models.user import User
from ..schemas.job import (
    JobCreatedResponse,
    JobDescriptionInput,
    JobDescriptionResponse,
    JobListResponse,
    JobProfileResponse,
)


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


SUPPORTED_JOB_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def _profile_response(
    profile: JobProfileModel,
) -> JobProfileResponse:
    return JobProfileResponse(
        id=profile.id,
        job_id=profile.job_id,
        title=profile.title,
        required_skills=profile.required_skills,
        preferred_skills=profile.preferred_skills,
        minimum_experience_years=(
            profile.minimum_experience_years
        ),
        education_requirements=(
            profile.education_requirements
        ),
        responsibilities=profile.responsibilities,
        evidence=profile.evidence,
    )


def _job_response(
    job: Job,
) -> JobDescriptionResponse:
    return JobDescriptionResponse(
        id=job.id,
        text=job.raw_text,
        created_at=job.created_at,
    )


def _set_anonymous_cookie(
    response: Response,
    job_id: int,
) -> None:
    is_production = (
        os.getenv("APP_ENV") == "production"
    )

    response.set_cookie(
        key=ANONYMOUS_SCREENING_COOKIE,
        value=create_anonymous_screening_token(job_id),
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )


def _create_job_from_text(
    db: Session,
    user_id: int | None,
    text: str,
    response: Response,
) -> JobCreatedResponse:
    """Create a job and extract its canonical profile."""

    job = Job(
        user_id=user_id,
        raw_text=text,
    )

    db.add(job)
    db.flush()

    try:
        extracted_profile = extract_job_profile(
            job.raw_text
        )

        profile = JobProfileModel(
            job_id=job.id,
            title=extracted_profile.title,
            required_skills=[
                skill.model_dump(mode="json")
                for skill in extracted_profile.required_skills
            ],
            preferred_skills=[
                skill.model_dump(mode="json")
                for skill in extracted_profile.preferred_skills
            ],
            minimum_experience_years=(
                extracted_profile.minimum_experience_years
            ),
            education_requirements=(
                extracted_profile.education_requirements
            ),
            responsibilities=(
                extracted_profile.responsibilities
            ),
            evidence=[
                evidence.model_dump(mode="json")
                for evidence in extracted_profile.evidence
            ],
        )

        db.add(profile)
        db.commit()

        db.refresh(job)
        db.refresh(profile)

        if user_id is None:
            _set_anonymous_cookie(
                response,
                job.id,
            )

        return JobCreatedResponse(
            job=_job_response(job),
            profile=_profile_response(profile),
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract the job description.",
        ) from exc


@router.post(
    "",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_job_description(
    job_input: JobDescriptionInput,
    response: Response,
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> JobCreatedResponse:
    """Create a job from pasted job-description text."""

    return _create_job_from_text(
        db=db,
        user_id=(
            current_user.id
            if current_user is not None
            else None
        ),
        text=job_input.text,
        response=response,
    )


@router.post(
    "/upload",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_job_description(
    response: Response,
    file: UploadFile = File(...),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> JobCreatedResponse:
    """Create a job from an uploaded PDF, DOCX, or TXT file."""

    filename = file.filename or "job-description"
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_JOB_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. "
                "Supported formats: PDF, DOCX, TXT."
            ),
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded job description is empty.",
        )

    temporary_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name

        parsed_document = parse_document(
            temporary_path
        )

    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass

    if parsed_document.parse_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                parsed_document.error
                or "Failed to extract text from the job description."
            ),
        )

    return _create_job_from_text(
        db=db,
        user_id=(
            current_user.id
            if current_user is not None
            else None
        ),
        text=parsed_document.raw_text,
        response=response,
    )


@router.get(
    "",
    response_model=JobListResponse,
)
def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobListResponse:
    """
    Return screening history for the authenticated recruiter.

    Anonymous screenings are intentionally excluded.
    """

    jobs = (
        db.query(Job)
        .filter(
            Job.user_id == current_user.id
        )
        .order_by(Job.created_at.desc())
        .all()
    )

    return JobListResponse(
        jobs=[
            _job_response(job)
            for job in jobs
        ]
    )


@router.get(
    "/{job_id}",
    response_model=JobDescriptionResponse,
)
def get_job_description(
    job_id: int,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
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

    return _job_response(job)


@router.get(
    "/{job_id}/profile",
    response_model=JobProfileResponse,
)
def get_job_profile(
    job_id: int,
    anonymous_token: str | None = Cookie(
        default=None,
        alias=ANONYMOUS_SCREENING_COOKIE,
    ),
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    db: Session = Depends(get_db),
) -> JobProfileResponse:
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

    profile = (
        db.query(JobProfileModel)
        .filter(
            JobProfileModel.job_id == job.id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job profile not found.",
        )

    return _profile_response(profile)