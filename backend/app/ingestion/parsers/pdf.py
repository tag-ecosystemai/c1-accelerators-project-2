import os

import pymupdf

from ..models import ParsedDocument


def parse_pdf(file_path: str) -> ParsedDocument:
    """Extract text from a PDF file, page by page."""

    page_map: dict[int, str] = {}
    full_text_parts: list[str] = []

    with pymupdf.open(file_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text()

            page_map[page_number] = page_text
            full_text_parts.append(page_text)

        page_count = len(doc)

    return ParsedDocument(
        source_filename=os.path.basename(file_path),
        raw_text="\n".join(full_text_parts),
        page_map=page_map,
        metadata={"page_count": page_count},
        parse_status="success",
    )