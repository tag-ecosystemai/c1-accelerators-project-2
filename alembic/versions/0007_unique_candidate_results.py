"""Add unique candidate/job constraint.

Revision ID: 0007_unique_candidate_results
Revises: 0006_add_job_ownership
"""

from alembic import op


revision = "0007_unique_candidate_results"
down_revision = "0006_add_job_ownership"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table(
        "candidate_results"
    ) as batch_op:
        batch_op.create_unique_constraint(
            "uq_candidate_results_candidate_job",
            [
                "candidate_id",
                "job_id",
            ],
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "candidate_results"
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_candidate_results_candidate_job",
            type_="unique",
        )