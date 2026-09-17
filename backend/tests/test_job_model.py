from sqlalchemy import inspect

from backend.app.database import engine
from backend.app.models.job import Job


def test_jobs_table_exists():
    inspector = inspect(engine)

    assert "jobs" in inspector.get_table_names()