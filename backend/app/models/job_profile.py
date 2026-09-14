from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class JobProfile(Base):
    __tablename__ = "job_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        unique=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    required_skills: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    minimum_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_requirements: Mapped[list[str]] = mapped_column(JSON, default=list)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
