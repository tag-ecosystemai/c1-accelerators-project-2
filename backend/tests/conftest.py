"""Shared fixtures that isolate backend tests from local PostgreSQL data."""

import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite://"

import pytest
from sqlalchemy import delete

from backend.app.database import Base, engine
from backend.app.models.job import Job
from backend.app.models.job_profile import JobProfile


Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database() -> None:
    """Start every test with an empty, in-memory database."""
    with engine.begin() as connection:
        connection.execute(delete(JobProfile))
        connection.execute(delete(Job))
    yield
    with engine.begin() as connection:
        connection.execute(delete(JobProfile))
        connection.execute(delete(Job))
