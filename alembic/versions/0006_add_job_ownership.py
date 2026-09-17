"""Add job ownership.

Revision ID: 0006_add_job_ownership
Revises: 0005_add_candidates
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_add_job_ownership"
down_revision = "0005_add_candidates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.add_column(
            sa.Column(
                "user_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_jobs_user_id",
            ["user_id"],
        )

        batch_op.create_foreign_key(
            "fk_jobs_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.drop_constraint(
            "fk_jobs_user_id_users",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_jobs_user_id",
        )

        batch_op.drop_column(
            "user_id",
        )