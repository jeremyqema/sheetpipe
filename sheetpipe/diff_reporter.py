"""Format and emit diff results for human or machine consumption."""

from __future__ import annotations

import json
from typing import TextIO
import sys

from sheetpipe.diff import DiffResult


def _truncate_row(row: list, max_cols: int = 5) -> str:
    """Return a compact string representation of a row, truncating if needed."""
    display = row[:max_cols]
    suffix = " ..." if len(row) > max_cols else ""
    return "[" + ", ".join(str(v) for v in display) + "]" + suffix


def format_text_diff(result: DiffResult, table: str = "<table>") -> str:
    """Return a human-readable text summary of a DiffResult."""
    lines = [f"Diff summary for '{table}':",
             f"  + {len(result.added)} added",
             f"  - {len(result.removed)} removed",
             f"  = {len(result.unchanged)} unchanged"]

    if result.added:
        lines.append("Added rows (up to 5):")
        for row in result.added[:5]:
            lines.append(f"  + {_truncate_row(row)}")

    if result.removed:
        lines.append("Removed rows (up to 5):")
        for row in result.removed[:5]:
            lines.append(f"  - {_truncate_row(row)}")

    return "\n".join(lines)


def format_json_diff(result: DiffResult, table: str = "<table>") -> str:
    """Return a JSON string representation of a DiffResult."""
    payload = {
        "table": table,
        "summary": result.summary,
        "added": result.added,
        "removed": result.removed,
    }
    return json.dumps(payload, indent=2)


def report_diff(
    result: DiffResult,
    table: str = "<table>",
    fmt: str = "text",
    stream: TextIO | None = None,
) -> None:
    """Print a diff report to *stream* (defaults to stdout)."""
    if stream is None:
        stream = sys.stdout

    if fmt == "json":
        output = format_json_diff(result, table)
    else:
        output = format_text_diff(result, table)

    print(output, file=stream)
