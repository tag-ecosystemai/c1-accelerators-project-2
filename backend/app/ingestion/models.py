from typing import Optional, Dict

from pydantic import BaseModel, Field


class ParsedDocument(BaseModel):
    """The output of parsing one uploaded file (resume or job description).

    This is the single contract between your ingestion code and everyone
    downstream (intelligence/, evidence/, api/). Keep it stable — changing
    field names later means changing everyone else's code too.
    """

    source_filename: str

    # The full extracted text. This is what intelligence/extractor.py's
    # extract_job_profile() and extract_candidate_profile() actually consume —
    # they take a plain string and do their own section-splitting internally.
    raw_text: str

    # Maps page_number -> text found on that page. DOCX/TXT have no real
    # concept of "pages", so this is None for those file types. Nothing
    # downstream reads this yet, but the PRD requires page-level evidence
    # eventually, so we capture it now while we have it.
    page_map: Optional[Dict[int, str]] = None

    # Anything else useful: file size, page count, extraction warnings, etc.
    metadata: dict = Field(default_factory=dict)

    # "success" or "failed" — lets batch processing report per-file status
    # without one bad file crashing the whole batch.
    parse_status: str = "success"
    error: Optional[str] = None