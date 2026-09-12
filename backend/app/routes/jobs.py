from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.job import Job
from ..schemas.job import JobDescriptionInput, JobDescriptionResponse


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