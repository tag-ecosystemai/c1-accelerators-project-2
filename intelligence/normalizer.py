import re

from intelligence.skills import SKILL_ALIASES


def normalize_text(text: str) -> str:
    """Normalize general text for consistent comparison."""

    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_skill(skill: str) -> str:
    """Normalize a skill name using the project's skill aliases."""

    normalized = normalize_text(skill)

    return SKILL_ALIASES.get(normalized, normalized)


def normalize_skill_list(skills: list[str]) -> list[str]:
    """Normalize skills and remove duplicates while preserving order."""

    normalized_skills: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized = normalize_skill(skill)

        if normalized and normalized not in seen:
            normalized_skills.append(normalized)
            seen.add(normalized)

    return normalized_skills