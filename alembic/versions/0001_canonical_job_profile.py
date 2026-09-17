"""Create the foundation schema and align job profiles with the canonical contract.

Revision ID: 0001_canonical_job_profile
Revises:
Create Date: 2026-09-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_canonical_job_profile"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "jobs" not in tables:
        op.create_table(
            "jobs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("raw_text", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if "job_profiles" not in tables:
        op.create_table(
            "job_profiles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "job_id",
                sa.Integer(),
                sa.ForeignKey("jobs.id"),
                nullable=False,
                unique=True,
            ),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("required_skills", sa.JSON(), nullable=False),
            sa.Column("preferred_skills", sa.JSON(), nullable=False),
            sa.Column(
                "minimum_experience_years",
                sa.Float(),
                nullable=True,
            ),
            sa.Column("education_requirements", sa.JSON(), nullable=False),
            sa.Column("responsibilities", sa.JSON(), nullable=False),
            sa.Column("evidence", sa.JSON(), nullable=False),
        )
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("job_profiles")
    }

    with op.batch_alter_table("job_profiles") as batch:
        if "title" not in columns:
            batch.add_column(
                sa.Column(
                    "title",
                    sa.String(length=255),
                    nullable=True,
                )
            )

        if "required_skills" not in columns:
            batch.add_column(
                sa.Column(
                    "required_skills",
                    sa.JSON(),
                    nullable=False,
                    server_default="[]",
                )
            )

        if "preferred_skills" not in columns:
            batch.add_column(
                sa.Column(
                    "preferred_skills",
                    sa.JSON(),
                    nullable=False,
                    server_default="[]",
                )
            )

        if "minimum_experience_years" not in columns:
            batch.add_column(
                sa.Column(
                    "minimum_experience_years",
                    sa.Float(),
                    nullable=True,
                )
            )

        if "education_requirements" not in columns:
            batch.add_column(
                sa.Column(
                    "education_requirements",
                    sa.JSON(),
                    nullable=False,
                    server_default="[]",
                )
            )

        if "responsibilities" not in columns:
            batch.add_column(
                sa.Column(
                    "responsibilities",
                    sa.JSON(),
                    nullable=False,
                    server_default="[]",
                )
            )

        if "evidence" not in columns:
            batch.add_column(
                sa.Column(
                    "evidence",
                    sa.JSON(),
                    nullable=True,
                )
            )

        if "title" in columns:
            batch.alter_column(
                "title",
                existing_type=sa.String(length=255),
                nullable=True,
            )

        if "experience_requirements" in columns:
            batch.drop_column("experience_requirements")

        if "other_requirements" in columns:
            batch.drop_column("other_requirements")
