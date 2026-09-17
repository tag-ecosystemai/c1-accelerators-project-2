"""add sessions table

Revision ID: 0004_add_sessions
Revises: 0003_add_users
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_add_sessions"
down_revision = "0003_add_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "token_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )

    op.create_index(
        "ix_sessions_token_hash",
        "sessions",
        ["token_hash"],
        unique=True,
    )

    op.create_index(
        "ix_sessions_user_id",
        "sessions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sessions_user_id",
        table_name="sessions",
    )

    op.drop_index(
        "ix_sessions_token_hash",
        table_name="sessions",
    )

    op.drop_table("sessions")