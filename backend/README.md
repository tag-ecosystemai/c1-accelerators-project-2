# TalentMatch AI Backend

## Overview

This backend persists job descriptions and the canonical structured profile produced by the intelligence module. It does not perform extraction, matching, scoring, or LLM explanations.

## Technology Stack

- Python 3.11
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Alembic
- Psycopg
- Pytest

## Current API

- `GET /health` checks that the service is running.
- `POST /jobs` saves original job-description text in `Job.raw_text`.
- `GET /jobs` lists saved job descriptions.
- `GET /jobs/{job_id}` returns one job description.
- `POST /jobs/{job_id}/profile` stores a canonical structured profile for a job.
- `GET /jobs/{job_id}/profile` returns that profile.

Only one profile may be created for each job. A duplicate request returns `409 Conflict`; an unknown job returns `404 Not Found`.

## Canonical Job Profile Contract

The backend imports `intelligence.models.JobProfile` rather than maintaining a second profile contract. A profile contains:

- Optional `title`.
- Required and preferred `Skill` objects, including `name`, `normalized_name`, `required`, and skill-level `evidence`.
- Optional `minimum_experience_years`.
- Education requirements and responsibilities.
- General profile `evidence`.

The original job-description text remains only in `Job.raw_text`; it is not duplicated in a profile.

## Local Setup

1. Use Python 3.11 and create a virtual environment.

```cmd
py -3.11 -m venv talentmatch-env
talentmatch-env\Scripts\activate.bat
```

2. Install the shared project dependencies.

```cmd
python -m pip install -r requirements.txt
```

3. Create a `.env` file at the project root.

```text
DATABASE_URL=postgresql+psycopg://talentmatch:YOUR_PASSWORD@localhost:5432/talentmatch
```

Never commit `.env`, because it contains credentials.

4. Apply database migrations.

```cmd
python -m alembic upgrade head
```

5. Start the API.

```cmd
python -m uvicorn backend.app.main:app --reload
```

The documentation is available at `http://127.0.0.1:8000/docs`.

## Tests

```cmd
python -m pytest
```

Tests use an isolated in-memory SQLite database. They do not read from or modify the local PostgreSQL database.

## Next Steps

- Connect the flow: raw job description → intelligence extraction → canonical `JobProfile` → persistence.
- Add Alembic migrations for future schema changes; `create_all()` remains only as a foundation helper.
- Integrate resume ingestion, matching, scoring, ranking, and evidence-backed explanations in separate work.
