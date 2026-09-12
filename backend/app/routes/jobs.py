from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.job import Job
from ..models.job_profile import JobProfile as JobProfileModel
from ..schemas.job import (
    JobDescriptionInput,
    JobDescriptionResponse,
    JobListResponse,
    JobProfile,
    JobProfileResponse,
)


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_job_description(
    job_input: JobDescriptionInput,
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    job = Job(raw_text=job_input.text)

    db.add(job)
    db.commit()
    db.refresh(job)

    return JobDescriptionResponse(
        id=job.id,
        text=job.raw_text,
        created_at=job.created_at,
    )


@router.get("/{job_id}", response_model=JobDescriptionResponse)
def get_job_description(
    job_id: int,
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    return JobDescriptionResponse(
        id=job.id,
        text=job.raw_text,
        created_at=job.created_at,
    )

def test_list_job_descriptions_returns_saved_jobs():
    client.post(
        "/jobs",
        json={"text": "Python Backend Engineer"},
    )

    response = client.get("/jobs")

    assert response.status_code == 200
    assert len(response.json()["jobs"]) >= 1

@router.get("", response_model=JobListResponse)
def list_job_descriptions(
    db: Session = Depends(get_db),
) -> JobListResponse:
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()

    return JobListResponse(
        jobs=[
            JobDescriptionResponse(
                id=job.id,
                text=job.raw_text,
                created_at=job.created_at,
            )
            for job in jobs
        ]
    )

@router.post(
    "/{job_id}/profile",
    response_model=JobProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job_profile(
    job_id: int,
    profile_input: JobProfile,
    db: Session = Depends(get_db),
) -> JobProfileResponse:
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    profile = JobProfileModel(
        job_id=job_id,
        title=profile_input.title,
        required_skills=profile_input.required_skills,
        preferred_skills=profile_input.preferred_skills,
        experience_requirements=profile_input.experience_requirements,
        education_requirements=profile_input.education_requirements,
        responsibilities=profile_input.responsibilities,
        other_requirements=profile_input.other_requirements,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return JobProfileResponse(
        id=profile.id,
        job_id=profile.job_id,
        title=profile.title,
        raw_text=job.raw_text,
        required_skills=profile.required_skills,
        preferred_skills=profile.preferred_skills,
        experience_requirements=profile.experience_requirements,
        education_requirements=profile.education_requirements,
        responsibilities=profile.responsibilities,
        other_requirements=profile.other_requirements,
    )
