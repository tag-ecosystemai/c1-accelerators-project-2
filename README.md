#TAG AI Engineering Bootcamp: Cohort 1
##Team Accelerators — Project 2
This repository contains Team Accelerators' work for Project 2 of the TAG AI Engineering Bootcamp.

##Team Members
Yifieyeh Achesomie Goni
SOULEY Raquib
Tomoloju Temilolaoluwa
Iyamokuma Inatimi
Aishat Adebanjo
Monday Imeobong

##Mentor
Assigned Mentor: God'sgift Olomu

##Program
TAG AI Engineering Bootcamp — Cohort 1

# TalentMatch AI

TalentMatch AI is a local-first, explainable resume-to-job matching engine designed to support recruiters in screening and reviewing candidates.

The system combines deterministic candidate matching and scoring with grounded LLM explanations.

> **Core principle:** The matching engine determines candidate fit; the LLM explains the evidence behind the result.

TalentMatch AI is a **recruiter decision-support system**, not an autonomous hiring system. Candidate scores and rankings are determined by deterministic matching logic, while human review remains part of the recruitment workflow.

---

## Project Status

TalentMatch AI is being developed as **Project 2 of the TAG Ecosystem AI Engineering Bootcamp**.

The repository currently contains:

* Recruiter-facing React frontend.
* Document intelligence and structured extraction.
* Skill normalization and evidence extraction.
* Semantic skill matching using local embeddings.
* Deterministic candidate scoring.
* Candidate ranking.
* FastAPI backend foundation.
* PostgreSQL database support.
* Alembic migrations.
* Backend and intelligence tests.

The remaining work is focused on integrating the individual modules into the complete end-to-end screening workflow.

---

## Architecture

```text
                         TalentMatch AI
                              │
              ┌───────────────┴───────────────┐
              │                               │
         React Frontend                  FastAPI Backend
              │                               │
              │                     ┌─────────┴─────────┐
              │                     │                   │
              │                Job / Candidate      Persistence
              │                  Processing           PostgreSQL
              │
              ▼
       Recruiter Workflow
              │
              ▼
      Job Description + Resumes
              │
              ▼
       Document / Text Processing
              │
              ▼
       Intelligence Extraction
              │
              ├── JobProfile
              └── CandidateProfile
              │
              ▼
       Skill Normalization
              │
              ▼
        Matching Engine
              │
              ├── Exact / normalized matching
              └── Semantic matching
              │
              ▼
       Deterministic Scoring
              │
              ├── Required Skills       40%
              ├── Relevant Experience   25%
              ├── Responsibilities      15%
              ├── Education             10%
              └── Preferred Skills      10%
              │
              ▼
       Candidate Ranking
              │
              ▼
       Evidence + Skill Gaps
              │
              ▼
       Grounded LLM Explanation
              │
              ▼
        Recruiter Review
```

---

## Repository Structure

```text
c1-accelerators-project-2/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
│
├── intelligence/
│   ├── models.py
│   ├── extractor.py
│   ├── skills.py
│   └── normalizer.py
│
├── matching/
│   ├── embeddings.py
│   ├── similarity.py
│   ├── matcher.py
│   ├── models.py
│   ├── pipeline.py
│   └── ranking.py
│
├── scoring/
│   └── scorer.py
│
├── ingestion/
├── evidence/
├── llm/
├── evaluation/
├── docs/
├── scripts/
├── data/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Core Modules

## Intelligence

The `intelligence/` module converts extracted document text into canonical structured profiles.

```text
Raw text
   ↓
Section detection
   ↓
Pattern-based extraction
   ↓
Skill detection
   ↓
Skill normalization
   ↓
Evidence collection
   ↓
JobProfile / CandidateProfile
```

The canonical domain models are defined in:

```text
intelligence/models.py
```

They include:

* `Evidence`
* `Skill`
* `JobProfile`
* `CandidateProfile`

The intelligence layer is responsible for extracting information. It does not determine candidate rankings.

---

## Matching

The `matching/` module determines whether candidate skills satisfy job requirements.

Matching supports:

* Exact skill matching.
* Normalized skill matching.
* Semantic similarity matching.
* Matched, partial, and missing statuses.
* Candidate evidence preservation.
* Skill gap generation.

The semantic matching model is:

```text
BAAI/bge-small-en-v1.5
```

with 384-dimensional embeddings.

Semantic similarity can identify a partial match, but semantic similarity alone does not automatically produce a fully matched status.

---

## Scoring

The `scoring/` module produces deterministic candidate scores.

The scoring weights are:

| Criterion                  | Weight |
| -------------------------- | -----: |
| Required Skills            |    40% |
| Relevant Experience        |    25% |
| Responsibilities Alignment |    15% |
| Education                  |    10% |
| Preferred Skills           |    10% |

The total candidate score is determined by these deterministic components.

The frontend must display these results rather than independently calculating them.

---

## Ranking

Candidate ranking is performed from deterministic score results.

The LLM is **not involved in ranking**.

Candidates with equal scores retain their input ordering through stable sorting.

---

## Backend

The `backend/` module provides the FastAPI API and database persistence layer.

### Technology

* Python 3.11
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* Psycopg
* Alembic
* Pytest

### Current API

#### Health

```text
GET /health
```

Checks that the API is running.

#### Job descriptions

```text
POST /jobs
GET /jobs
GET /jobs/{job_id}
```

Job descriptions are stored as original text in:

```text
Job.raw_text
```

#### Job profiles

```text
POST /jobs/{job_id}/profile
GET /jobs/{job_id}/profile
```

Only one structured profile can currently be associated with each job.

A duplicate profile request returns:

```text
409 Conflict
```

An unknown job or profile returns:

```text
404 Not Found
```

---

## Canonical Job Profile Contract

The backend imports:

```python
from intelligence.models import JobProfile
```

rather than maintaining a second independent profile contract.

A `JobProfile` contains:

* Optional title.
* Required `Skill` objects.
* Preferred `Skill` objects.
* Skill-level evidence.
* Minimum experience requirement.
* Education requirements.
* Responsibilities.
* General profile evidence.

Each skill preserves:

```text
name
normalized_name
required
evidence
```

Each evidence item preserves:

```text
text
location
```

The original job description remains in `Job.raw_text` and is not duplicated inside the structured profile.

---

# Database

The backend uses:

* PostgreSQL for application persistence.
* SQLAlchemy for ORM/database access.
* Alembic for schema migrations.

The current schema includes:

```text
jobs
job_profiles
```

Database schema changes should be made through Alembic migrations rather than relying on `Base.metadata.create_all()` for production schema management.

`create_all()` is retained only as a development/test foundation helper where appropriate.

---

# Frontend

The recruiter-facing frontend is built with:

* React
* TypeScript
* Vite
* CSS
* ESLint

The frontend currently uses mock data while backend services are being integrated.

## Recruiter Workflow

```text
Landing
   │
   ▼
Screening Setup
   │
   │ Run Candidate Screening
   ▼
Candidate Dashboard
   │
   ├───────────────┐
   │               │
   ▼               ▼
Candidate Review   Candidate Comparison
   │               │
   │               ▼
   │        AI Comparison Summary
   ▼
Grounded AI Explanation
```

### Screening Setup

Recruiters can:

* Enter a job title.
* Paste a job description.
* Upload a job description.
* Upload multiple candidate resumes.
* Start the screening workflow.

### Candidate Dashboard

The dashboard provides:

* Extracted job requirements.
* Candidate ranking.
* Overall fit score.
* Required skill coverage.
* Matched skills.
* Missing skills.
* Candidate processing status.
* Candidate search.
* Minimum score filtering.
* Required skill coverage filtering.

Frontend filtering does not recalculate or modify candidate ranking.

### Candidate Review

Candidate-level review includes:

* Overall fit score.
* Required skill coverage.
* Deterministic score breakdown.
* Required skills.
* Relevant experience.
* Responsibilities alignment.
* Education.
* Preferred skills.
* Skill match status.
* Resume evidence.
* Skill gaps.
* Grounded LLM explanation.

The interface explicitly communicates that the LLM does not determine candidate scores or rankings.

### Candidate Comparison

Recruiters can select up to three candidates and compare them side by side.

Comparison includes:

* Overall fit.
* Required skill coverage.
* Preferred skill coverage.
* Relevant experience.
* Education.
* Responsibilities alignment.
* Matched skills.
* Major skill gaps.
* Supporting evidence.
* AI comparison summary.

Comparison is displayed only after the recruiter explicitly selects candidates and chooses **Compare selected**.

---

# LLM Explanations

TalentMatch uses Groq for grounded explanations.

The LLM is responsible for:

* Explaining deterministic matching results.
* Summarizing supporting evidence.
* Explaining candidate strengths.
* Highlighting skill gaps.
* Generating candidate comparison summaries.

The LLM must **not**:

* Calculate candidate scores.
* Modify candidate scores.
* Determine candidate ranking.
* Invent resume evidence.
* Infer protected or sensitive characteristics.

The LLM receives the deterministic results and supporting evidence produced by the matching system.

---

# Responsible AI

TalentMatch AI is a recruiter decision-support system.

The system is designed so that:

* Candidate fit is determined by deterministic matching logic.
* Candidate rankings are deterministic.
* LLM output is explanatory rather than authoritative.
* Evidence remains traceable to source documents.
* Missing evidence is not silently treated as proof of absence.
* Protected or sensitive characteristics are not used for candidate scoring.
* Human review remains part of the recruitment process.

The system does not make autonomous hiring decisions.

---

# Requirements

Install:

* Python 3.11
* Node.js
* npm
* PostgreSQL for local database development

Verify Python:

```powershell
python --version
```

Verify Node.js and npm:

```powershell
node --version
npm --version
```

---

# Backend Setup

From the repository root:

## 1. Create a virtual environment

```powershell
py -3.11 -m venv talentmatch-env
```

Activate it:

```powershell
.\talentmatch-env\Scripts\Activate.ps1
```

## 2. Install shared dependencies

```powershell
python -m pip install -r requirements.txt
```

## 3. Configure environment variables

Create a `.env` file in the repository root.

Example:

```text
DATABASE_URL=postgresql+psycopg://talentmatch:YOUR_PASSWORD@localhost:5432/talentmatch
```

Never commit `.env`.

Use `.env.example` as the template for required environment variables.

## 4. Apply database migrations

```powershell
python -m alembic upgrade head
```

## 5. Start the API

```powershell
python -m uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

From the repository root:

Install dependencies:

```powershell
npm --prefix frontend install
```

Start the Vite development server:

```powershell
npm --prefix frontend run dev
```

The frontend will normally be available at:

```text
http://localhost:5173/
```

Vite provides Hot Module Replacement during development.

---

# Testing

Run the complete Python test suite from the repository root:

```powershell
python -m pytest
```

Backend tests use an isolated SQLite database rather than the developer's local PostgreSQL database.

Migration tests use a separate temporary database to validate the Alembic migration path.

The test suite covers areas including:

* Intelligence extraction.
* Skill normalization.
* Evidence extraction.
* Matching.
* Semantic similarity.
* Deterministic scoring.
* Candidate ranking.
* Matching pipeline.
* Backend database behavior.
* API validation.
* Job endpoints.
* Job profile endpoints.
* Database migrations.

---

# Frontend Validation

Run ESLint:

```powershell
npm --prefix frontend run lint
```

Build the frontend:

```powershell
npm --prefix frontend run build
```

Both should complete successfully before submitting frontend changes.

---

# Development Workflow

Development should be performed on feature branches rather than directly on `main`.

Create a branch:

```powershell
git checkout -b feat/describe-change
```

Make the changes and validate them.

For backend changes:

```powershell
python -m pytes
```
