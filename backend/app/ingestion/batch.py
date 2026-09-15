from .dispatcher import parse_resume
from .models import ParsedDocument


def process_batch(file_paths: list[str]) -> list[ParsedDocument]:
    """Parse multiple files while isolating individual failures."""

    results: list[ParsedDocument] = []

    for file_path in file_paths:
        results.append(parse_resume(file_path))

    return results


def batch_summary(results: list[ParsedDocument]) -> dict[str, object]:
    """Return a summary of successful and failed document processing."""

    succeeded = [
        result
        for result in results
        if result.parse_status == "success"
    ]

    failed = [
        result
        for result in results
        if result.parse_status == "failed"
    ]

    return {
        "total": len(results),
        "succeeded": len(succeeded),
        "failed": len(failed),
        "failed_files": [
            {
                "file": result.source_filename,
                "error": result.error,
            }
            for result in failed
        ],
    }