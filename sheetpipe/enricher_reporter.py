"""Format and print enrichment result reports."""
from __future__ import annotations

import json
from typing import IO, Literal

from sheetpipe.enricher import EnrichmentResult


def format_text_enrichment_report(result: EnrichmentResult) -> str:
    lines = ["=== Enrichment Report ==="]
    if result.enriched_columns:
        cols = ", ".join(result.enriched_columns)
        lines.append(f"Added columns  : {cols}")
    else:
        lines.append("Added columns  : (none)")
    lines.append(f"Total rows     : {len(result.rows)}")
    if result.warnings:
        lines.append(f"Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            lines.append(f"  - {w}")
    else:
        lines.append("Warnings       : none")
    return "\n".join(lines)


def format_json_enrichment_report(result: EnrichmentResult) -> str:
    payload = {
        "enriched_columns": result.enriched_columns,
        "total_rows": len(result.rows),
        "warning_count": len(result.warnings),
        "warnings": result.warnings,
    }
    return json.dumps(payload, indent=2)


def report_enrichment(
    result: EnrichmentResult,
    fmt: Literal["text", "json"] = "text",
    stream: IO[str] | None = None,
) -> str:
    import sys

    out = stream or sys.stdout
    text = (
        format_text_enrichment_report(result)
        if fmt == "text"
        else format_json_enrichment_report(result)
    )
    print(text, file=out)
    return text
