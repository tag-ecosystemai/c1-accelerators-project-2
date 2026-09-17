import re

from intelligence.models import (
    CandidateProfile,
    Evidence,
    JobProfile,
    Skill,
)
from intelligence.normalizer import normalize_skill
from intelligence.skills import (
    AMBIGUOUS_SKILL_ALIASES,
    SKILL_ALIASES,
)


AMBIGUOUS_SKILL_CONTEXTS: dict[str, list[str]] = {
    "ai": [
        r"\bai\s+(?:systems?|models?|tools?|solutions?|applications?|platforms?)",
        r"\bai[-\s]powered\b",
        r"\bai[-\s]driven\b",
        r"\bai[-\s]based\b",
        r"\bexperience\s+(?:with|in)\s+ai\b",
        r"\b(?:developed|built|worked with|used|implemented)\s+ai\b",
    ],
    "go": [
        r"\bgo\s+(?:programming|language)\b",
        r"\bprogramming\s+in\s+go\b",
        r"\bexperience\s+(?:with|in)\s+go\b",
        r"\b(?:developed|built|worked with|used|implemented)\s+(?:applications?|services?|systems?)\s+(?:using|in)\s+go\b",
    ],
    "rest": [
        r"\brest\s+api(?:s)?\b",
        r"\brestful\s+api(?:s)?\b",
        r"\brest[-\s]based\s+(?:api|services?)\b",
        r"\bexperience\s+(?:with|in)\s+rest\b",
        r"\b(?:developed|built|worked with|used|implemented)\s+rest\b",
    ],
}


def extract_skills(
    text: str,
    required: bool = False,
    dedicated_section: bool = False,
) -> list[Skill]:
    """Extract recognized skills and preserve supporting evidence."""

    extracted: dict[str, Skill] = {}

    for sentence_match in re.finditer(
        r"[^.!?\n]+(?:[.!?]|(?=\n)|$)",
        text,
    ):
        sentence = sentence_match.group(0).strip()

        if not sentence:
            continue

        normalized_sentence = sentence.lower()

        for alias, canonical_name in sorted(
            SKILL_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

            if not re.search(pattern, normalized_sentence):
                continue

            if (
                alias in AMBIGUOUS_SKILL_ALIASES
                and not dedicated_section
            ):
                continue

            normalized_name = normalize_skill(alias)

            skill = extracted.get(normalized_name)

            if skill is None:
                extracted[normalized_name] = Skill(
                    name=alias,
                    normalized_name=normalized_name,
                    required=required,
                    evidence=[
                        Evidence(text=sentence)
                    ],
                )
                continue

            existing_evidence = {
                evidence.text
                for evidence in skill.evidence
            }

            if sentence not in existing_evidence:
                skill.evidence.append(
                    Evidence(text=sentence)
                )

    return list(extracted.values())


ALL_SECTION_HEADINGS = {
    # Job description sections
    "required skills",
    "required qualifications",
    "requirements",
    "must have",
    "must-have",
    "essential skills",
    "preferred skills",
    "preferred qualifications",
    "nice to have",
    "nice-to-have",
    "desired skills",
    "responsibilities",
    "key responsibilities",
    "duties",
    "what you'll do",
    "what you will do",
    "role responsibilities",
    "education",
    "educational requirements",
    "academic qualifications",

    # Resume sections
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "work history",
    "education",
    "educational background",
    "academic background",
    "academic qualifications",
    "qualifications",
    "projects",
    "personal projects",
    "academic projects",
    "selected projects",
    "skills",
    "technical skills",
    "core skills",
    "technical competencies",
    "competencies",
    "responsibilities",
    "key responsibilities",
    "duties",
    "achievements",
}


def _normalize_heading(line: str) -> str:
    """Normalize a possible section heading for comparison."""

    return re.sub(
        r"[:\s]+$",
        "",
        line.strip().lower(),
    )


def _is_section_heading(line: str) -> bool:
    """Determine whether a line is a known document section heading."""

    normalized = _normalize_heading(line)

    if normalized in ALL_SECTION_HEADINGS:
        return True

    return (
        line.strip().isupper()
        and 1 <= len(line.strip().split()) <= 6
    )


def _extract_section(text: str, headings: list[str]) -> str:
    """Extract text belonging to a specific document section."""

    lines = text.splitlines()

    target_headings = {
        _normalize_heading(heading)
        for heading in headings
    }

    section_lines: list[str] = []
    collecting = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if collecting:
                section_lines.append("")
            continue

        normalized_line = _normalize_heading(stripped)

        if not collecting:
            if normalized_line in target_headings:
                collecting = True

            continue

        if _is_section_heading(stripped):
            break

        section_lines.append(stripped)

    return "\n".join(section_lines).strip()


def _extract_title(text: str) -> str | None:
    """Extract a likely job title from the beginning of a job description."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    title_patterns = [
        r"^job title\s*:\s*(.+)$",
        r"^position\s*:\s*(.+)$",
        r"^role\s*:\s*(.+)$",
    ]

    for line in lines[:10]:
        for pattern in title_patterns:
            match = re.match(
                pattern,
                line,
                re.IGNORECASE,
            )

            if match:
                return match.group(1).strip()

    return lines[0]


def _extract_experience_requirement(text: str) -> float | None:
    """Extract the minimum required years of experience from a job description."""

    required_patterns = [
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s+years?",
        r"at\s+least\s+(\d+(?:\.\d+)?)\s*\+?\s+years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s+years?\s+of\s+experience\s+required",
        r"(\d+(?:\.\d+)?)\s*\+?\s+years?\s+of\s+professional\s+experience\s+required",
    ]

    for pattern in required_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return float(match.group(1))

    generic_pattern = (
        r"(\d+(?:\.\d+)?)\s*\+\s+years?"
        r"\s+(?:of\s+)?(?:professional\s+)?experience"
    )

    for match in re.finditer(
        generic_pattern,
        text,
        re.IGNORECASE,
    ):
        start, end = match.span()

        context = text[max(0, start - 80): end + 80].lower()

        if re.search(
            r"\b(preferred|prefer|desired|bonus|plus|nice\s+to\s+have)\b",
            context,
        ):
            continue

        return float(match.group(1))

    return None


def _extract_list_items(section: str) -> list[str]:
    """Convert a section into clean individual items."""

    items: list[str] = []

    for line in section.splitlines():
        cleaned = line.strip()

        if not cleaned:
            continue

        cleaned = re.sub(
            r"^[•\-\*\u2022]\s*",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"^\d+[\.)]\s*",
            "",
            cleaned,
        )

        if cleaned:
            items.append(cleaned)

    return items


def _deduplicate_skills(skills: list[Skill]) -> list[Skill]:
    """Remove duplicate normalized skills while preserving evidence."""

    unique: dict[str, Skill] = {}

    for skill in skills:
        existing = unique.get(skill.normalized_name)

        if existing is None:
            unique[skill.normalized_name] = skill
            continue

        existing_evidence = {
            evidence.text
            for evidence in existing.evidence
        }

        for evidence in skill.evidence:
            if evidence.text not in existing_evidence:
                existing.evidence.append(evidence)
                existing_evidence.add(evidence.text)

    return list(unique.values())


def _remove_required_from_preferred(
    required_skills: list[Skill],
    preferred_skills: list[Skill],
) -> list[Skill]:
    """Remove skills from preferred when they are also required."""

    required_names = {
        skill.normalized_name
        for skill in required_skills
    }

    return [
        skill
        for skill in preferred_skills
        if skill.normalized_name not in required_names
    ]


def extract_job_profile(text: str) -> JobProfile:
    """Extract a structured job profile from raw job-description text."""

    required_section = _extract_section(
        text,
        [
            "required skills",
            "required qualifications",
            "requirements",
            "must have",
            "must-have",
            "essential skills",
        ],
    )

    preferred_section = _extract_section(
        text,
        [
            "preferred skills",
            "preferred qualifications",
            "nice to have",
            "nice-to-have",
            "desired skills",
        ],
    )

    responsibilities_section = _extract_section(
        text,
        [
            "responsibilities",
            "key responsibilities",
            "duties",
            "what you'll do",
            "what you will do",
            "role responsibilities",
        ],
    )

    education_section = _extract_section(
        text,
        [
            "education",
            "educational requirements",
            "qualifications",
            "academic qualifications",
        ],
    )

    required_skills = extract_skills(
        required_section,
        required=True,
        dedicated_section=True,
    )

    preferred_skills = extract_skills(
        preferred_section,
        required=False,
        dedicated_section=True,
    )

    contextual_required = _extract_contextual_skills(
        text,
        required=True,
    )

    contextual_preferred = _extract_contextual_skills(
        text,
        required=False,
    )

    required_skills.extend(contextual_required)
    preferred_skills.extend(contextual_preferred)

    required_skills = _deduplicate_skills(required_skills)
    preferred_skills = _deduplicate_skills(preferred_skills)

    preferred_skills = _remove_required_from_preferred(
        required_skills,
        preferred_skills,
    )

    responsibilities = _extract_list_items(
        responsibilities_section
    )

    education_requirements = _extract_list_items(
        education_section
    )

    return JobProfile(
        title=_extract_title(text),
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        minimum_experience_years=_extract_experience_requirement(text),
        education_requirements=education_requirements,
        responsibilities=responsibilities,
        evidence=[
            Evidence(text=text.strip())
        ] if text.strip() else [],
    )


def _extract_contact_info(
    text: str,
) -> tuple[str | None, str | None]:
    """Extract email address and phone number from resume text."""

    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    phone_match = re.search(
        r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)",
        text,
    )

    email = (
        email_match.group(0)
        if email_match
        else None
    )

    phone = (
        phone_match.group(0).strip()
        if phone_match
        else None
    )

    return email, phone


def _extract_candidate_name(text: str) -> str | None:
    """Extract a likely candidate name from the beginning of a resume."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    email_pattern = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    for line in lines[:8]:
        if email_pattern.search(line):
            continue

        if any(char.isdigit() for char in line):
            continue

        words = line.split()

        if 2 <= len(words) <= 4:
            return line

    return lines[0]


def _extract_experience_years(
    text: str,
) -> float | None:
    """Estimate total experience from explicit years-of-experience statements."""

    pattern = (
        r"(\d+(?:\.\d+)?)\+?\s+years?"
        r"\s+(?:of\s+)?(?:professional\s+)?experience"
    )

    matches = [
        float(match.group(1))
        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE,
        )
    ]

    if not matches:
        return None

    return max(matches)


CANDIDATE_SECTION_HEADINGS = {
    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "selected projects",
    ],
    "responsibilities": [
        "responsibilities",
        "key responsibilities",
        "duties",
        "achievements",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "technical competencies",
        "competencies",
    ],
}


def _build_section_evidence(
    section: str,
    location: str,
) -> list[Evidence]:
    """Convert extracted section items into general candidate evidence."""

    evidence: list[Evidence] = []

    for item in _extract_list_items(section):
        evidence.append(
            Evidence(
                text=item,
                location=location,
            )
        )

    return evidence


def extract_candidate_profile(
    text: str,
) -> CandidateProfile:
    """Extract a structured candidate profile from resume text."""

    email, phone = _extract_contact_info(text)

    skills_section = _extract_section(
        text,
        CANDIDATE_SECTION_HEADINGS["skills"],
    )

    education_section = _extract_section(
        text,
        CANDIDATE_SECTION_HEADINGS["education"],
    )

    experience_section = _extract_section(
        text,
        CANDIDATE_SECTION_HEADINGS["experience"],
    )

    projects_section = _extract_section(
        text,
        CANDIDATE_SECTION_HEADINGS["projects"],
    )

    responsibilities_section = _extract_section(
        text,
        CANDIDATE_SECTION_HEADINGS["responsibilities"],
    )

    skills = extract_skills(
        skills_section,
        dedicated_section=True,
    )

    evidence = (
        _build_section_evidence(
            experience_section,
            "experience",
        )
        + _build_section_evidence(
            education_section,
            "education",
        )
        + _build_section_evidence(
            projects_section,
            "projects",
        )
        + _build_section_evidence(
            responsibilities_section,
            "responsibilities",
        )
    )

    return CandidateProfile(
        name=_extract_candidate_name(text),
        email=email,
        phone=phone,
        skills=skills,
        experience_years=_extract_experience_years(text),
        education=_extract_list_items(education_section),
        employment_history=_extract_list_items(experience_section),
        projects=_extract_list_items(projects_section),
        responsibilities=_extract_list_items(
            responsibilities_section
        ),
        evidence=evidence,
    )


def _extract_contextual_skills(
    text: str,
    required: bool,
) -> list[Skill]:
    """Extract skills from sentences that indicate requirement level."""

    extracted: list[Skill] = []
    seen: set[str] = set()

    requirement_patterns = (
        [
            r"\brequired\b",
            r"\bmust\s+(?:have|possess|know|be)\b",
            r"\bneed(?:s|ed)?\s+(?:to\s+)?(?:have|possess|know)\b",
            r"\bshould\s+have\b",
            r"\bessential\b",
            r"\bmandatory\b",
        ]
        if required
        else [
            r"\bpreferred\b",
            r"\bprefer(?:red)?\b",
            r"\bnice\s+to\s+have\b",
            r"\bdesired\b",
            r"\bbonus\b",
            r"\bplus\b",
        ]
    )

    for sentence_match in re.finditer(
        r"[^.!?\n]+(?:[.!?]|(?=\n)|$)",
        text,
    ):
        sentence = sentence_match.group(0).strip()

        if not sentence:
            continue

        normalized_sentence = sentence.lower()

        if not any(
            re.search(pattern, normalized_sentence)
            for pattern in requirement_patterns
        ):
            continue

        for alias, canonical_name in sorted(
            SKILL_ALIASES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            skill_pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

            if not re.search(
                skill_pattern,
                normalized_sentence,
            ):
                continue

            if (
                alias in AMBIGUOUS_SKILL_ALIASES
                and not any(
                    re.search(
                        context_pattern,
                        normalized_sentence,
                    )
                    for context_pattern in AMBIGUOUS_SKILL_CONTEXTS.get(
                        alias,
                        [],
                    )
                )
            ):
                continue

            if canonical_name in seen:
                continue

            extracted.append(
                Skill(
                    name=alias,
                    normalized_name=canonical_name,
                    required=required,
                    evidence=[
                        Evidence(text=sentence)
                    ],
                )
            )

            seen.add(canonical_name)

    return extracted