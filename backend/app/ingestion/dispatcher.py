import os

from .models import ParsedDocument
from .parsers.pdf import parse_pdf
from .parsers.docx import parse_docx
from .parsers.txt import parse_txt


def parse_resume(file_path: str) -> ParsedDocument:
    """Parse any supported file type into a ParsedDocument.

    This is the ONLY function the rest of the app needs to call. It never
    raises an exception, and it never reports success for a document that
    yielded no usable text (empty file, image-only PDF, etc.) — downstream
    NLP has nothing to work with in that case, so it's treated as a failure.
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
    except Exception as e:
        # Catches corrupted files, password-protected files, permission
        # errors, malformed DOCX zips, etc.
        return ParsedDocument(
            source_filename=filename,
            raw_text="",
            parse_status="failed",
            error=str(e),
        )

    # A file that technically "parses" but yields no usable text (empty
    # file, blank/image-only scanned PDF) should not be reported as a
    # success — there's nothing here for the NLP stage to extract.
    if not result.raw_text.strip():
        result.parse_status = "failed"
        result.error = result.error or (
            "No extractable text found (document may be empty, "
            "image-only, or a scanned file without OCR)."
        )

    return result