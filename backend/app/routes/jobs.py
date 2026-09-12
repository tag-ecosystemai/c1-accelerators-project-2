from fastapi import APIRouter

from ..schemas.job import JobDescriptionInput


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("")
def submit_job_description(job: JobDescriptionInput) -> JobDescriptionInput:
    return job