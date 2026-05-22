"""Column enrichment: add computed columns derived from existing row data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass
class EnrichmentConfig:
    """Defines a single computed column to append to each row."""
    column_name: str
    expression: Callable[[dict], Optional[str]]
    default: Optional[str] = None


@dataclass
class EnrichmentResult:
    headers: List[str]
    rows: List[List[str]]
    enriched_columns: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def kept_count(result: EnrichmentResult) -> int:
    return len(result.rows)


def _row_to_dict(headers: List[str], row: List[str]) -> dict:
    return {h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)}


def enrich_rows(
    headers: List[str],
    rows: List[List[str]],
    configs: List[EnrichmentConfig],
) -> EnrichmentResult:
    """Apply each EnrichmentConfig to produce new columns appended to every row."""
    if not configs:
        return EnrichmentResult(headers=list(headers), rows=[list(r) for r in rows])

    new_headers = list(headers) + [c.column_name for c in configs]
    enriched_columns = [c.column_name for c in configs]
    new_rows: List[List[str]] = []
    warnings: List[str] = []

    for idx, row in enumerate(rows):
        row_dict = _row_to_dict(headers, row)
        new_row = list(row)
        for cfg in configs:
            try:
                value = cfg.expression(row_dict)
                new_row.append(str(value) if value is not None else (cfg.default or ""))
            except Exception as exc:  # noqa: BLE001
                warnings.append(
                    f"Row {idx}: enrichment '{cfg.column_name}' failed: {exc}"
                )
                new_row.append(cfg.default or "")
        new_rows.append(new_row)

    return EnrichmentResult(
        headers=new_headers,
        rows=new_rows,
        enriched_columns=enriched_columns,
        warnings=warnings,
    )
