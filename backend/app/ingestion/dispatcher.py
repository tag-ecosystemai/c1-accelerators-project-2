import os

from .models import ParsedDocument
from .parsers.docx import parse_docx
from .parsers.pdf import parse_pdf
from .parsers.txt import parse_txt


def parse_document(file_path: str) -> ParsedDocument:
    """Parse a supported document into a ParsedDocument.

    Parsing failures are converted into a structured failed result so that
    callers can handle invalid documents without an unhandled exception.
    """

    filename = os.path.basename(file_path)
    extension = os.path.splitext(file_path)[1].lower()

    try:
        if extension == ".pdf":
            result = parse_pdf(file_path)
        elif extension == ".docx":
            result = parse_docx(file_path)
        elif extension == ".txt":
            result = parse_txt(file_path)
        else:
            return ParsedDocument(
                source_filename=filename,
                raw_text="",
                parse_status="failed",
                error=f"Unsupported file type: {extension}",
            )
    except Exception as exc:
        return ParsedDocument(
            source_filename=filename,
            raw_text="",
            parse_status="failed",
            error=str(exc),
        )

    if not result.raw_text.strip():
        result.parse_status = "failed"
        result.error = result.error or (
            "No extractable text found (document may be empty, "
            "image-only, or a scanned file without OCR)."
        )

    return result


def parse_resume(file_path: str) -> ParsedDocument:
    """Parse a resume using the shared document parser.

    Kept as a compatibility wrapper for the existing candidate pipeline.
    """

    return parse_document(file_path)