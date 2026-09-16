"""
TalentMatch AI — Evidence Grounding
Location: evidence/ (shared, top-level — not owned by any single pipeline stage)

Locates supporting text for a claim inside a parsed document's sections.
Pulled out of intelligence/resume_extraction.py because evidence/ exists as
its own top-level folder in the repo, sibling to intelligence/, matching/,
and scoring/ — a sign this is meant to be shared infrastructure, not
private logic duplicated inside whichever module happens to need it first.

Any stage that needs to ground a claim in source text can import
`find_evidence` from here: intelligence/ for skills/employment/education/
projects, and potentially matching/ or scoring/ if they ever need to
justify a score with a snippet directly.

Decoupling note: this module intentionally does NOT import
ParsedResumeDocument (or any concrete document type) from intelligence/ or
ingestion/. It accepts anything with the right shape (source_document,
full_text, sections) via the HasSections protocol below, so evidence/ has
no dependency on any other pipeline-stage package. Once ingestion/ (Tomoloju)
defines its real parsed-document contract, callers just pass that in — no
change needed here as long as the shape matches.
"""

from __future__ import annotations

from typing import Optional, Protocol

from backend.app.schemas import Evidence


class _Section(Protocol):
    text: str
    heading: Optional[str]
    page_number: Optional[int]


class HasSections(Protocol):
    """Structural type for whatever ingestion/ ultimately returns."""
    source_document: str
    full_text: str
    sections: list


class _FullTextSection:
    """Fallback wrapper used when a document has no section breakdown at all."""

    def __init__(self, text: str):
        self.text = text
        self.heading: Optional[str] = None
        self.page_number: Optional[int] = None


def find_evidence(query: str, doc: HasSections, associated_field: Optional[str] = None) -> list[Evidence]:
    """
    Locate a supporting snippet for `query` inside the document's parsed
    sections. Returns [] if nothing matches — an explicit no-evidence
    result rather than a guessed one (PRD §6.4: no evidence found is not
    the same as proven absence, but it must still be recorded honestly).

    This is exact (case-insensitive) substring matching, not semantic —
    deliberately so, since fabricated-looking "close enough" evidence is a
    bigger risk than an occasional missed match. Paraphrased claims won't
    find a snippet; that's a known limitation, not a bug.
    """
    if not query:
        return []
    needle = query.lower().strip()
    sections = doc.sections or [_FullTextSection(doc.full_text)]

    for section in sections:
        text = getattr(section, "text", "")
        idx = text.lower().find(needle)
        if idx == -1:
            continue
        start = max(0, idx - 40)
        end = min(len(text), idx + len(query) + 40)
        snippet = text[start:end].strip()
        return [Evidence(
            source_document=doc.source_document,
            section=getattr(section, "heading", None),
            page_number=getattr(section, "page_number", None),
            text_snippet=snippet,
            associated_field=associated_field,
        )]
    return []


if __name__ == "__main__":
    class _FakeDoc:
        source_document = "sample.pdf"
        full_text = "Skills: Python, PostgreSQL"
        sections = [_FullTextSection("Skills: Python, PostgreSQL")]

    result = find_evidence("Python", _FakeDoc(), associated_field="Python")
    assert result and result[0].text_snippet
    assert find_evidence("Rust", _FakeDoc()) == []
    print("Evidence grounding smoke tests passed.")
