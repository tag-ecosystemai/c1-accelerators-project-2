from sqlalchemy import inspect

from backend.app.database import engine
from backend.app.models.job_profile import JobProfile


def test_job_profiles_table_exists():
    inspector = inspect(engine)

    assert "job_profiles" in inspector.get_table_names()