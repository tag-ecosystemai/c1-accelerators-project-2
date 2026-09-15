from .database import Base, engine
from .models.job import Job
from .models.job_profile import JobProfile

Base.metadata.create_all(bind=engine)