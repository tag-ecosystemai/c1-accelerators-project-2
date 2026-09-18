"""
TalentMatch AI — Skill Normalization Layer
Owner: Monday Imeobong (NLP / Information Extraction & Skill Intelligence Engineer)

Resolves raw skill mentions (aliases, abbreviations, spelling variants) to a
canonical form, and classifies how a candidate's skill relates to a JD's
required/preferred skill.

Scope note: semantic/embedding similarity (BAAI/bge-small-en-v1.5) is
Iyamokuma's layer, not this one. This module only ever returns
MatchConfidence.RELATED for pairs in the curated RELATED_SKILLS graph below
— it never calls an embedding model. That keeps "curated related" auditable
and independent of the embedding-based semantic step downstream.
"""

from __future__ import annotations

import difflib
import re

from backend.app.schemas import MatchConfidence, Skill

# ---------------------------------------------------------------------------
# Canonical skill taxonomy
# ---------------------------------------------------------------------------
# Every known alias/abbreviation/spelling variant -> canonical name.
# Keys are matched after lowercasing + whitespace/punctuation cleanup —
# don't rely on exact casing when adding entries.

_ALIASES: dict[str, str] = {
    # Frontend
    "react": "React", "react.js": "React", "reactjs": "React",
    "vue": "Vue.js", "vuejs": "Vue.js", "vue.js": "Vue.js",
    "next": "Next.js", "next.js": "Next.js", "nextjs": "Next.js",
    "ts": "TypeScript", "typescript": "TypeScript",
    "js": "JavaScript", "javascript": "JavaScript", "ecmascript": "JavaScript",

    # Backend / languages
    "py": "Python", "python": "Python", "python3": "Python",
    "node": "Node.js", "node.js": "Node.js", "nodejs": "Node.js",
    "golang": "Go", "go": "Go",

    # Data / ML
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "dl": "Deep Learning", "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing", "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision", "computer vision": "Computer Vision",
    "llm": "Large Language Models", "llms": "Large Language Models",

    # Databases
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "psql": "PostgreSQL",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "mysql": "MySQL",

    # Cloud / infra
    "aws": "AWS", "amazon web services": "AWS",
    "gcp": "GCP", "google cloud": "GCP", "google cloud platform": "GCP",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "docker": "Docker",

    # Other common ones
    "rest": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs", "restful api": "REST APIs",
    "ci/cd": "CI/CD", "cicd": "CI/CD",
}

# Curated "related but not equivalent" relationships — symmetric, undirected.
# Feeds MatchConfidence.RELATED only; never promoted to EXACT.
_RELATED_SKILLS: dict[str, set[str]] = {
    "React": {"JavaScript", "TypeScript", "Vue.js", "Next.js"},
    "Vue.js": {"JavaScript", "TypeScript", "React"},
    "Next.js": {"React", "JavaScript", "TypeScript"},
    "Node.js": {"JavaScript", "TypeScript"},
    "Machine Learning": {"Deep Learning", "Python", "Natural Language Processing", "Computer Vision"},
    "Deep Learning": {"Machine Learning", "Natural Language Processing", "Computer Vision"},
    "Natural Language Processing": {"Machine Learning", "Deep Learning", "Large Language Models"},
    "PostgreSQL": {"MySQL", "MongoDB"},
    "AWS": {"GCP", "Docker", "Kubernetes"},
    "Docker": {"Kubernetes", "CI/CD"},
    "Kubernetes": {"Docker", "AWS", "GCP"},
}

_CANONICAL_NAMES: set[str] = set(_ALIASES.values()) | set(_RELATED_SKILLS.keys())


def _clean(text: str) -> str:
    """Lowercase, collapse whitespace, strip trailing punctuation for lookup."""
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[.,;:]+$", "", text)
    return text


def normalize(raw_skill: str, fuzzy_cutoff: float = 0.85) -> str:
    """
    Resolve a raw skill mention to its canonical name.

    Lookup order:
      1. Exact alias table match (handles known variants/abbreviations).
      2. Fuzzy match against known canonical names (catches typos/minor
         spelling variants not explicitly listed — e.g. 'Pythonn').
      3. Fallback: return the input as-is, stripped. Unknown skills still
         get a consistent value rather than being silently dropped.

    fuzzy_cutoff is deliberately conservative (0.85) to avoid false
    positives like 'Go' matching 'Vue.js'. Tune against real resume data.
    """
    key = _clean(raw_skill)
    if key in _ALIASES:
        return _ALIASES[key]

    close = difflib.get_close_matches(raw_skill.strip(), _CANONICAL_NAMES, n=1, cutoff=fuzzy_cutoff)
    if close:
        return close[0]

    return raw_skill.strip()


def classify_match(candidate_raw_skill: str, jd_skill_normalized: str) -> MatchConfidence:
    """
    Classify how one candidate skill mention relates to one JD skill.

    Only ever returns EXACT or RELATED for a recognized relationship — this
    function has no notion of a JD skill the candidate never mentioned at
    all; callers are responsible for defaulting un-mentioned JD skills to
    MatchConfidence.NONE themselves (see PRD §6.4: no evidence is not proof
    of absence, but it's still recorded as NONE here).
    """
    candidate_normalized = normalize(candidate_raw_skill)

    if candidate_normalized == jd_skill_normalized:
        return MatchConfidence.EXACT

    if candidate_normalized in _RELATED_SKILLS.get(jd_skill_normalized, set()):
        return MatchConfidence.RELATED

    return MatchConfidence.NONE


def get_canonical_skills() -> set[str]:
    """Public accessor for the known canonical skill vocabulary (used by fallback scanners elsewhere)."""
    return set(_CANONICAL_NAMES)


def normalize_skill_list(raw_skills: list[str]) -> list[Skill]:
    """Convert flat raw skill strings (e.g. from LLM extraction) into deduplicated Skill objects."""
    seen: dict[str, Skill] = {}
    for raw in raw_skills:
        canonical = normalize(raw)
        if canonical not in seen:
            seen[canonical] = Skill(raw_text=raw, normalized_name=canonical)
    return list(seen.values())


if __name__ == "__main__":
    # Smoke test
    assert normalize("React.js") == "React"
    assert normalize("ReactJS") == "React"
    assert normalize("Postgres") == "PostgreSQL"
    assert normalize("Pythonn") == "Python"  # fuzzy fallback catches the typo

    assert classify_match("Vue.js", "React") == MatchConfidence.RELATED
    assert classify_match("React", "React") == MatchConfidence.EXACT
    assert classify_match("Docker", "React") == MatchConfidence.NONE

    skills = normalize_skill_list(["Python", "ML", "react.js", "React"])
    print([(s.raw_text, s.normalized_name) for s in skills])
    print("All smoke tests passed.")
