import os

import pymupdf  # modern import name; 'fitz' still works but is deprecated

from ..models import ParsedDocument


def parse_pdf(file_path: str) -> ParsedDocument:
    """Extract text from a PDF file, page by page."""

    doc = pymupdf.open(file_path)

    page_map: dict = {}
    full_text_parts: list = []

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text()
        page_map[page_number] = page_text
        full_text_parts.append(page_text)

    doc.close()

    return ParsedDocument(
        source_filename=os.path.basename(file_path),
        raw_text="\n".join(full_text_parts),
        page_map=page_map,
        metadata={"page_count": len(page_map)},
        parse_status="success",
    )