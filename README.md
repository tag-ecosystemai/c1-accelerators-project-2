# TAG AI Engineering Bootcamp: Cohort 1

## Team Accelerators — Project 2

This repository contains Team Accelerators' work for Project 2 of the TAG AI Engineering Bootcamp.

## Team Members

* Yifieyeh Achesomie Goni
* SOULEY Raquib
* Tomoloju Temilolaoluwa
* Iyamokuma Inatimi
* Aishat Adebanjo
* Monday Imeobong

## Mentor

**Assigned Mentor:** God'sgift Olomu

## Program

**TAG AI Engineering Bootcamp — Cohort 1**

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

### AI / LLM

* `BAAI/bge-small-en-v1.5` — embeddings
* `cross-encoder/ms-marco-MiniLM-L6-v2` — reranking
* Groq
* `openai/gpt-oss-20b` — grounded explanations

The LLM is used only to explain deterministic matching results.

---

## Architecture

```text
                    TalentMatch AI
                          │
          ┌───────────────┴───────────────┐
          │                               │
      Frontend                         Backend
   React + TypeScript                  FastAPI
          │                               │
          │                    ┌──────────┴──────────┐
          │                    │                     │
          │              Job/Resume           Matching Engine
          │              Processing                 │
          │                    │                    │
          │                    └──────────┬─────────┘
          │                               │
          │                       Scoring & Ranking
          │                               │
          │                               ▼
          │                       Evidence & Results
          │                               │
          │                               ▼
          │                       ExplanationService
          │                               │
          │                         LLMClient
          │                               │
          │                    ┌──────────┴──────────┐
          │                    │                     │
          │              MockLLMClient        GroqLLMClient
          │                                          │
          │                                  gpt-oss-20b
          │
          └────────────── API Responses ─────────────┘

                         PostgreSQL
                              │
                              ▼
                       Application Data
```

### Matching Flow

```text
Job Description
       ↓
Job Profile Extraction
       ↓
Resume Processing
       ↓
Skill & Evidence Extraction
       ↓
Exact / Normalized / Semantic Matching
       ↓
Weighted Scoring
       ↓
Candidate Ranking
       ↓
Candidate Review & Comparison
       ↓
Grounded LLM Explanation
```

The matching engine is responsible for the actual scoring and ranking. The LLM receives the resulting scores, evidence, matches, gaps, and breakdowns and generates an explanation based only on that information.

---

# How to Run

## Prerequisites

Install:

* Python 3.11+
* Node.js
* npm
* PostgreSQL

## 1. Clone the repository

```bash
git clone <repository-url>
cd c1-accelerators-project-2
```

## 2. Set up the backend

Create and activate a Python virtual environment:

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

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3. Configure environment variables

Create a `.env` file from `.env.example`.

## 4. Run database migrations

```bash
alembic upgrade head
```

## 5. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

## 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```
