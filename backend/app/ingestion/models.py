from typing import Literal

from pydantic import BaseModel, Field


class ParsedDocument(BaseModel):
    """Normalized output produced by a document parser."""

    source_filename: str
    raw_text: str
    page_map: dict[int, str] | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    parse_status: Literal["success", "failed"] = "success"
    error: str | None = None