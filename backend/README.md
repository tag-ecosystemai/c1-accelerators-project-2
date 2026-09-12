# TalentMatch AI Backend

## Overview

This backend provides the API and PostgreSQL persistence layer for TalentMatch AI, an explainable resume-to-job matching system.

The current implementation focuses on the job description workflow: saving job description text, storing structured job requirements, and making those resources available through the API.

## Technology Stack

- Python 3.13
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Psycopg
- Pytest

## Completed Features

- FastAPI application with automatic API documentation at `/docs`.
- Health check endpoint: `GET /health`.
- PostgreSQL connection configured through `DATABASE_URL`.
- Database tables for job descriptions and job profiles.
- Job description endpoints:
  - `POST /jobs` creates and saves job description text.
  - `GET /jobs` returns saved job descriptions, newest first.
  - `GET /jobs/{job_id}` returns one saved job description.
- Structured job profile endpoints:
  - `POST /jobs/{job_id}/profile` saves extracted job requirements.
  - `GET /jobs/{job_id}/profile` returns the saved structured profile.
  - Duplicate profiles for the same job description are rejected with `409 Conflict`.
- Automated test suite covering API routes, schemas, database connection, and database tables.

## Job Profile Data

A structured job profile contains:

- Job title
- Required skills
- Preferred skills
- Experience requirements
- Education requirements
- Responsibilities
- Other explicit requirements

## Local Setup

1. Create and activate the virtual environment.

```cmd
talentmatch-env\Scripts\activate.bat
```

2. Install dependencies.

```cmd
python -m pip install -r backend\requirements.txt
```

3. Create a `.env` file at the project root.

```text
DATABASE_URL=postgresql+psycopg://talentmatch:YOUR_PASSWORD@localhost:5432/talentmatch
```

Never commit the `.env` file because it contains secrets.

4. Create database tables.

```cmd
python -m backend.app.init_db
```

5. Start the API.

```cmd
python -m uvicorn backend.app.main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

## Run Tests

```cmd
python -m pytest
```

## Remaining P0 Work

- Integrate job-description extraction with the NLP module.
- Add resume batch upload and document-processing integration.
- Store candidate profiles, evidence, matches, and scores.
- Integrate deterministic matching and scoring.
- Add candidate ranking, detail, and comparison endpoints.
- Integrate grounded Groq explanations without allowing the LLM to determine scores or rankings.
- Add robust batch processing statuses and per-file error handling.
- Add evaluation endpoints and metrics support.

## Architecture Principle

The deterministic matching and scoring engine determines candidate fit and ranking. The LLM only explains evidence-backed results.
