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


def _normalize_skills(
    skills: object,
    required: bool,
) -> list[dict[str, object]]:
    """Convert valid legacy skills into the canonical Skill JSON shape."""
    if not isinstance(skills, list):
        return []

    normalized: list[dict[str, object]] = []

    for skill in skills:
        if isinstance(skill, str):
            name = skill.strip()

            if not name:
                continue

            normalized.append(
                {
                    "name": name,
                    "normalized_name": name.lower(),
                    "required": required,
                    "evidence": [],
                }
            )

        elif isinstance(skill, dict):
            name = skill.get("name")

            if not isinstance(name, str):
                continue

            name = name.strip()

            if not name:
                continue

            normalized_name = skill.get("normalized_name")

            if not isinstance(normalized_name, str):
                normalized_name = name.lower()
            else:
                normalized_name = normalized_name.strip().lower()

            if not normalized_name:
                normalized_name = name.lower()

            evidence = skill.get("evidence", [])

            if not isinstance(evidence, list):
                evidence = []

            normalized.append(
                {
                    "name": name,
                    "normalized_name": normalized_name,
                    "required": bool(skill.get("required", required)),
                    "evidence": evidence,
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
                required_skills=_normalize_skills(
                    row["required_skills"],
                    required=True,
                ),
                preferred_skills=_normalize_skills(
                    row["preferred_skills"],
                    required=False,
                ),
                evidence=(
                    row["evidence"]
                    if isinstance(row["evidence"], list)
                    else []
                ),
            )
        )

    with op.batch_alter_table("job_profiles") as batch:
        batch.alter_column(
            "evidence",
            existing_type=sa.JSON(),
            nullable=False,
        )