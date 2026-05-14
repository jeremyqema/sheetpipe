"""Simple validation reporter for sheetpipe pipeline runs."""
from __future__ import annotations

import json
import sys
from typing import TextIO

from sheetpipe.validator import ValidationResult


def report_validation(
    result: ValidationResult,
    *,
    table_name: str = "<unknown>",
    out: TextIO | None = None,
    fmt: str = "text",
) -> None:
    """Print a human-readable or JSON validation summary.

    Args:
        result: The ValidationResult to report on.
        table_name: Destination table name shown in the report.
        out: Output stream (defaults to stdout).
        fmt: ``"text"`` or ``"json"``.
    """
    out = out or sys.stdout

    if fmt == "json":
        payload = {
            "table": table_name,
            "valid_rows": len(result.valid_rows),
            "invalid_rows": result.error_count,
            "errors": [
                {"row_index": idx, "reason": reason}
                for idx, _row, reason in result.invalid_rows
            ],
        }
        out.write(json.dumps(payload, indent=2) + "\n")
        return

    out.write(f"[sheetpipe] Validation report for table '{table_name}'\n")
    out.write(f"  Valid rows  : {len(result.valid_rows)}\n")
    out.write(f"  Invalid rows: {result.error_count}\n")
    if result.has_errors:
        out.write("  Errors:\n")
        for idx, _row, reason in result.invalid_rows:
            out.write(f"    row {idx}: {reason}\n")
