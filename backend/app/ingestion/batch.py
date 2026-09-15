from .dispatcher import parse_resume
from .models import ParsedDocument


def process_batch(file_paths: list) -> list:
    """Parse a list of uploaded files. One failure never stops the rest."""

    results = []

    for path in file_paths:
        results.append(parse_resume(path))

    return results


def batch_summary(results: list) -> dict:
    """A quick status summary the frontend/API can show to the recruiter."""

    succeeded = [r for r in results if r.parse_status == "success"]
    failed = [r for r in results if r.parse_status == "failed"]

    return {
        "total": len(results),
        "succeeded": len(succeeded),
        "failed": len(failed),
        "failed_files": [
            {"file": r.source_filename, "error": r.error} for r in failed
        ],
    }