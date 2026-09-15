import os

from ..models import ParsedDocument


def parse_txt(file_path: str) -> ParsedDocument:
    """Read a plain text file."""

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    return ParsedDocument(
        source_filename=os.path.basename(file_path),
        raw_text=text,
        page_map=None,
        metadata={},
        parse_status="success",
    )