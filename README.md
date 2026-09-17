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

TalentMatch AI is a recruiter-facing, explainable resume-to-job matching platform.

It helps recruiters screen multiple resumes against a job description using deterministic matching, evidence-based scoring, and grounded LLM explanations.

> **Important:** TalentMatch AI is not an autonomous hiring system. The matching engine calculates scores and rankings deterministically. The LLM is used only to explain the supplied matching results. Recruiters remain responsible for hiring decisions.

---

## Features

* Job description upload or text input
* Job profile extraction
* Batch resume upload
* Resume parsing for PDF and DOCX files
* Deterministic candidate matching
* Exact and normalized skill matching
* Semantic matching
* Evidence-based matching results
* Weighted candidate scoring
* Candidate ranking
* Required-skill coverage
* Candidate detail and review
* Comparison of 2–3 candidates
* Grounded candidate explanations
* Grounded candidate comparison explanations
* Anonymous screening support
* Authenticated recruiter workflows

### Scoring

| Category            | Weight |
| ------------------- | -----: |
| Required Skills     |    40% |
| Relevant Experience |    25% |
| Responsibilities    |    15% |
| Education           |    10% |
| Preferred Skills    |    10% |

The deterministic matching engine owns the score and ranking. The LLM does not calculate, modify, or override them.

---

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* Alembic
* PyMuPDF
* python-docx
* Sentence Transformers
* pytest

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Lucide
* TanStack Table
* React Hook Form
* Zod

### LLM

TalentMatch uses a provider abstraction for explanations:

```text
Explanation API
      ↓
ExplanationService
      ↓
LLMClient
      ↓
MockLLMClient / GroqLLMClient
```

Local development and automated tests use the deterministic mock provider.

Production can use Groq with:

```text
openai/gpt-oss-20b
```

The LLM is only responsible for explaining deterministic matching results.

---

# Local Development

## Prerequisites

Install:

* Python 3.11+
* Node.js
* npm
* PostgreSQL

Docker can also be used to run PostgreSQL locally.

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd c1-accelerators-project-2
```

---

## 2. Create the Python environment

From the project root:

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a local `.env` file from `.env.example`.

```powershell
Copy-Item .env.example .env
```

Then configure the values for your local environment.

For local development, use:

```env
APP_ENV=development
APP_NAME=TalentMatch AI
DEBUG=true

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

DATABASE_URL=postgresql+psycopg://talentmatch:password@localhost:5432/talentmatch

LLM_PROVIDER=mock
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

FRONTEND_URL=http://localhost:5173

ANONYMOUS_SCREENING_SECRET=your_local_secret
```

### LLM provider

For local development:

```env
LLM_PROVIDER=mock
```

A Groq API key is **not required** when using the mock provider.

When Groq is configured for production:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env` or expose API keys in the frontend.

---

## 5. Start PostgreSQL

The repository includes a Docker Compose configuration for PostgreSQL.

From the project root:

```bash
docker compose up -d postgres
```

Verify the container is running:

```bash
docker ps
```

---

## 6. Run database migrations

From the project root:

```bash
alembic upgrade head
```

---

## 7. Start the backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

The backend runs at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

---

## 8. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

The frontend uses:

```env
VITE_API_BASE_URL=http://localhost:8000
```

If `VITE_API_BASE_URL` is not provided, the frontend defaults to `http://localhost:8000`.

For a deployed frontend, set `VITE_API_BASE_URL` to the deployed backend URL.

---

# Testing

## Backend tests

From the project root:

### Windows PowerShell

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests -q
```

The backend test suite covers authentication, jobs, candidates, matching, scoring, explanations, and API behavior.

## Frontend lint

```bash
cd frontend
npm run lint
```

## Frontend production build

```bash
npm run build
```

---

# LLM Explanation Architecture

Candidate explanations and candidate comparisons follow this flow:

```text
Frontend
   ↓
FastAPI explanation endpoint
   ↓
ExplanationService
   ↓
LLMClient
   ↓
MockLLMClient or GroqLLMClient
```

The deterministic matching engine supplies:

* scores
* rankings
* skill matches
* skill gaps
* evidence
* score breakdowns

The LLM receives these results and produces a grounded explanation.

The LLM must not:

* calculate a new score
* modify a score
* change candidate rankings
* recommend hiring or rejection
* invent candidate experience
* invent skills or evidence
* infer protected characteristics
* treat missing evidence as proof that a candidate lacks a skill

---

# Project Structure

```text
c1-accelerators-project-2/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   └── package.json
│
├── llm/
│   ├── __init__.py
│   ├── client.py
│   └── prompts.py
│
├── matching/
├── scoring/
├── intelligence/
├── ingestion/
├── evaluation/
├── evidence/
├── alembic/
├── data/
├── docs/
├── scripts/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Development Notes

### Local LLM testing

Team members do not need a Groq API key to run the project locally.

Use:

```env
LLM_PROVIDER=mock
```

This allows the complete explanation workflow to be tested without external API calls or Groq quota.

### Production LLM

Before production deployment, configure:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=<your-key>
GROQ_MODEL=openai/gpt-oss-20b
```

The API key must be configured as a server-side environment variable and must never be placed in the React frontend.

---

# Deployment

The planned production architecture is:

```text
Render
│
├── PostgreSQL
│
├── FastAPI Backend
│
└── React/Vite Frontend
```

The production backend will use the Render PostgreSQL database and the Groq LLM provider.

Deployment configuration is maintained separately from local development configuration.

---

# Team Workflow

Before pushing changes:

```bash
git status
```

Run backend tests:

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests -q
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

Then commit and push the changes.

Do not commit:

```text
.env
.venv/
node_modules/
```

Use `.env.example` as the shared environment-variable template.

---

# Project Status

TalentMatch AI currently supports the core recruiter workflow:

```text
Job Description
      ↓
Job Profile
      ↓
Resume Upload
      ↓
Candidate Processing
      ↓
Deterministic Matching
      ↓
Scoring & Ranking
      ↓
Candidate Review
      ↓
Candidate Comparison
      ↓
Grounded LLM Explanation
```

The local development environment can run the complete workflow using the mock LLM provider without requiring a Groq API key.
