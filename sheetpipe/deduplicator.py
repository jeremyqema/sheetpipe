"""Row deduplication utilities for sheetpipe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class DeduplicateResult:
    headers: List[str]
    rows: List[List[str]]
    duplicate_count: int = 0
    seen_keys: List[str] = field(default_factory=list)


def kept_count(result: DeduplicateResult) -> int:
    return len(result.rows)


def dropped_count(result: DeduplicateResult) -> int:
    return result.duplicate_count


def _row_key(row: List[str], key_columns: Optional[List[str]], headers: List[str]) -> str:
    """Build a hashable string key for a row based on specified columns or full row."""
    if not key_columns:
        return "|".join(row)
    indices = [headers.index(col) for col in key_columns if col in headers]
    return "|".join(row[i] if i < len(row) else "" for i in indices)


def deduplicate_rows(
    headers: List[str],
    rows: List[List[str]],
    key_columns: Optional[List[str]] = None,
    keep: str = "first",
) -> DeduplicateResult:
    """Remove duplicate rows, keeping either 'first' or 'last' occurrence.

    Args:
        headers: Column header names.
        rows: Data rows.
        key_columns: Columns to use as the dedup key. None means full row.
        keep: 'first' or 'last' — which occurrence to retain.

    Returns:
        DeduplicateResult with deduplicated rows and stats.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    source = rows if keep == "first" else list(reversed(rows))
    seen: dict[str, List[str]] = {}
    duplicate_count = 0

    for row in source:
        key = _row_key(row, key_columns, headers)
        if key in seen:
            duplicate_count += 1
        else:
            seen[key] = row

    ordered_keys = [_row_key(r, key_columns, headers) for r in rows]
    if keep == "first":
        deduped = [seen[k] for k in dict.fromkeys(ordered_keys)]
    else:
        deduped = [seen[k] for k in reversed(list(dict.fromkeys(reversed(ordered_keys))))]

    return DeduplicateResult(
        headers=headers,
        rows=deduped,
        duplicate_count=duplicate_count,
        seen_keys=list(seen.keys()),
    )
