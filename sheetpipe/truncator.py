"""truncator.py — truncate rows to a maximum count with optional offset."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TruncateConfig:
    limit: int
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ValueError(f"limit must be >= 0, got {self.limit}")
        if self.offset < 0:
            raise ValueError(f"offset must be >= 0, got {self.offset}")


@dataclass
class TruncateResult:
    headers: List[str]
    rows: List[List[str]]
    total_before: int
    dropped_count: int
    warnings: List[str] = field(default_factory=list)


def kept_count(result: TruncateResult) -> int:
    """Return the number of rows kept after truncation."""
    return len(result.rows)


def truncate_rows(
    headers: List[str],
    rows: List[List[str]],
    config: Optional[TruncateConfig] = None,
) -> TruncateResult:
    """Slice *rows* to at most *config.limit* entries starting at *config.offset*.

    If *config* is None the rows are returned unchanged.
    """
    total_before = len(rows)
    warnings: List[str] = []

    if config is None:
        return TruncateResult(
            headers=headers,
            rows=list(rows),
            total_before=total_before,
            dropped_count=0,
        )

    if config.offset >= total_before and total_before > 0:
        warnings.append(
            f"offset {config.offset} exceeds row count {total_before}; "
            "returning empty result"
        )

    sliced = rows[config.offset : config.offset + config.limit]
    dropped = total_before - len(sliced)

    return TruncateResult(
        headers=headers,
        rows=sliced,
        total_before=total_before,
        dropped_count=dropped,
        warnings=warnings,
    )
