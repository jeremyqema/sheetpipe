from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FlattenConfig:
    """Configuration for flattening a repeated-value column into multiple rows."""
    column: str
    delimiter: str = ","
    strip_whitespace: bool = True
    skip_empty_segments: bool = True


@dataclass
class FlattenResult:
    headers: List[str]
    rows: List[List[str]]
    original_row_count: int
    output_row_count: int
    warnings: List[str] = field(default_factory=list)

    @property
    def expansion_count(self) -> int:
        return self.output_row_count - self.original_row_count


def _col_index(headers: List[str], column: str) -> Optional[int]:
    try:
        return headers.index(column)
    except ValueError:
        return None


def flatten_rows(
    headers: List[str],
    rows: List[List[str]],
    config: FlattenConfig,
) -> FlattenResult:
    """Expand rows by splitting a delimited column into one row per segment."""
    warnings: List[str] = []
    idx = _col_index(headers, config.column)

    if idx is None:
        warnings.append(
            f"flatten: column '{config.column}' not found in headers; returning rows unchanged"
        )
        return FlattenResult(
            headers=headers,
            rows=rows,
            original_row_count=len(rows),
            output_row_count=len(rows),
            warnings=warnings,
        )

    output: List[List[str]] = []
    for row in rows:
        cell = row[idx] if idx < len(row) else ""
        segments = cell.split(config.delimiter)
        if config.strip_whitespace:
            segments = [s.strip() for s in segments]
        if config.skip_empty_segments:
            segments = [s for s in segments if s]
        if not segments:
            segments = [""]
        for segment in segments:
            new_row = list(row)
            # Pad short rows before assignment
            while len(new_row) <= idx:
                new_row.append("")
            new_row[idx] = segment
            output.append(new_row)

    return FlattenResult(
        headers=headers,
        rows=output,
        original_row_count=len(rows),
        output_row_count=len(output),
        warnings=warnings,
    )
