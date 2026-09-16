"""Add candidates and candidate results.

Revision ID: 0005_add_candidates
Revises: 0004_add_sessions
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_candidates"
down_revision = "0004_add_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_filename",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "raw_text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "profile",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "processing_status",
            sa.String(length=20),
            nullable=False,
            server_default="completed",
        ),
        sa.Column(
            "error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_candidates_job_id",
        "candidates",
        ["job_id"],
    )

    op.create_table(
        "candidate_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "match_result",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "score_breakdown",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_candidate_results_candidate_id",
        "candidate_results",
        ["candidate_id"],
    )

    op.create_index(
        "ix_candidate_results_job_id",
        "candidate_results",
        ["job_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_candidate_results_job_id",
        table_name="candidate_results",
    )
    op.drop_index(
        "ix_candidate_results_candidate_id",
        table_name="candidate_results",
    )
    op.drop_table("candidate_results")

    op.drop_index(
        "ix_candidates_job_id",
        table_name="candidates",
    )
    op.drop_table("candidates")