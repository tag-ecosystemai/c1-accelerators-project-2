import os

from ingestion.models import ParsedDocument
from ingestion.parsers.pdf import parse_pdf
from ingestion.parsers.docx import parse_docx
from ingestion.parsers.txt import parse_txt


def parse_resume(file_path: str) -> ParsedDocument:
    """Parse any supported file type into a ParsedDocument.

    This is the ONLY function the rest of the app needs to call. It never
    raises an exception — if parsing fails, it returns a ParsedDocument
    with parse_status="failed" instead. This is what stops one bad resume
    from crashing an entire batch upload.
    """

    extension = os.path.splitext(file_path)[1].lower()

    try:
        if extension == ".pdf":
            return parse_pdf(file_path)
        elif extension == ".docx":
            return parse_docx(file_path)
        elif extension == ".txt":
            return parse_txt(file_path)
        else:
            return ParsedDocument(
                source_filename=file_path,
                raw_text="",
                parse_status="failed",
                error=f"Unsupported file type: {extension}",
            )
    except Exception as e:
        # Catches things like: corrupted PDF, password-protected file,
        # empty file, permission errors, etc.
        return ParsedDocument(
            source_filename=file_path,
            raw_text="",
            parse_status="failed",
            error=str(e),
        )