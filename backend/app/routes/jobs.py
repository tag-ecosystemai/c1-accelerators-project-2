"""HTTP endpoints for storing job descriptions and canonical job profiles."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from intelligence.models import JobProfile

from ..database import get_db
from ..models.job import Job
from ..models.job_profile import JobProfile as JobProfileModel
from ..schemas.job import JobDescriptionInput, JobDescriptionResponse, JobListResponse, JobProfileResponse


router = APIRouter(prefix="/jobs", tags=["jobs"])


def _profile_response(profile: JobProfileModel) -> JobProfileResponse:
    """Convert persisted JSON data back to the canonical API contract."""
    return JobProfileResponse(
        id=profile.id,
        job_id=profile.job_id,
        title=profile.title,
        required_skills=profile.required_skills,
        preferred_skills=profile.preferred_skills,
        minimum_experience_years=profile.minimum_experience_years,
        education_requirements=profile.education_requirements,
        responsibilities=profile.responsibilities,
        evidence=profile.evidence,
    )


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def submit_job_description(job_input: JobDescriptionInput, db: Session = Depends(get_db)) -> JobDescriptionResponse:
    job = Job(raw_text=job_input.text)
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobDescriptionResponse(id=job.id, text=job.raw_text, created_at=job.created_at)


@router.get("/{job_id}", response_model=JobDescriptionResponse)
def get_job_description(job_id: int, db: Session = Depends(get_db)) -> JobDescriptionResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
    return JobDescriptionResponse(id=job.id, text=job.raw_text, created_at=job.created_at)


@router.get("", response_model=JobListResponse)
def list_job_descriptions(db: Session = Depends(get_db)) -> JobListResponse:
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return JobListResponse(
        jobs=[JobDescriptionResponse(id=job.id, text=job.raw_text, created_at=job.created_at) for job in jobs]
    )


@router.post("/{job_id}/profile", response_model=JobProfileResponse, status_code=status.HTTP_201_CREATED)
def create_job_profile(job_id: int, profile_input: JobProfile, db: Session = Depends(get_db)) -> JobProfileResponse:
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")

    existing_profile = db.query(JobProfileModel).filter(JobProfileModel.job_id == job_id).first()
    if existing_profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job profile already exists.")

    profile = JobProfileModel(
        job_id=job_id,
        title=profile_input.title,
        required_skills=[skill.model_dump(mode="json") for skill in profile_input.required_skills],
        preferred_skills=[skill.model_dump(mode="json") for skill in profile_input.preferred_skills],
        minimum_experience_years=profile_input.minimum_experience_years,
        education_requirements=profile_input.education_requirements,
        responsibilities=profile_input.responsibilities,
        evidence=[evidence.model_dump(mode="json") for evidence in profile_input.evidence],
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _profile_response(profile)


@router.get("/{job_id}/profile", response_model=JobProfileResponse)
def get_job_profile(job_id: int, db: Session = Depends(get_db)) -> JobProfileResponse:
    profile = db.query(JobProfileModel).filter(JobProfileModel.job_id == job_id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job profile not found.")
    return _profile_response(profile)
