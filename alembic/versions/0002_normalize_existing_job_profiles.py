"""Normalize legacy profile JSON before enforcing the canonical contract.

Revision ID: 0002_normalize_profiles
Revises: 0001_canonical_job_profile
Create Date: 2026-09-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_normalize_profiles"
down_revision = "0001_canonical_job_profile"
branch_labels = None
depends_on = None


def _normalize_skills(skills: object, required: bool) -> list[dict[str, object]]:
    """Convert legacy string skills into the canonical Skill JSON shape."""
    if not isinstance(skills, list):
        return []
    normalized: list[dict[str, object]] = []
    for skill in skills:
        if isinstance(skill, str):
            normalized.append(
                {
                    "name": skill,
                    "normalized_name": skill.strip().lower(),
                    "required": required,
                    "evidence": [],
                }
            )
        elif isinstance(skill, dict):
            normalized.append(
                {
                    "name": skill.get("name", ""),
                    "normalized_name": skill.get("normalized_name", skill.get("name", "").strip().lower()),
                    "required": skill.get("required", required),
                    "evidence": skill.get("evidence", []),
                }
            )
    return normalized


def upgrade() -> None:
    bind = op.get_bind()
    profiles = sa.table(
        "job_profiles",
        sa.column("id", sa.Integer()),
        sa.column("required_skills", sa.JSON()),
        sa.column("preferred_skills", sa.JSON()),
        sa.column("evidence", sa.JSON()),
    )
    rows = bind.execute(sa.select(profiles)).mappings()
    for row in rows:
        bind.execute(
            profiles.update()
            .where(profiles.c.id == row["id"])
            .values(
                required_skills=_normalize_skills(row["required_skills"], required=True),
                preferred_skills=_normalize_skills(row["preferred_skills"], required=False),
                evidence=row["evidence"] or [],
            )
        )

    with op.batch_alter_table("job_profiles") as batch:
        batch.alter_column("evidence", existing_type=sa.JSON(), nullable=False)
