from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_canonical_schema(tmp_path):
    database_path = tmp_path / "migration_test.db"
    database_url = f"sqlite+pysqlite:///{database_path}"

    project_root = Path(__file__).resolve().parents[2]

    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)

    try:
        inspector = inspect(engine)

        assert "jobs" in inspector.get_table_names()
        assert "job_profiles" in inspector.get_table_names()

        job_columns = {
            column["name"]
            for column in inspector.get_columns("jobs")
        }

        profile_columns = {
            column["name"]
            for column in inspector.get_columns("job_profiles")
        }

        assert job_columns == {
            "id",
            "user_id",
            "raw_text",
            "created_at",
        }

        assert {
            "id",
            "job_id",
            "title",
            "required_skills",
            "preferred_skills",
            "minimum_experience_years",
            "education_requirements",
            "responsibilities",
            "evidence",
        }.issubset(profile_columns)
    finally:
        engine.dispose()