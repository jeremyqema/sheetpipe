"""Row sorting utilities for sheetpipe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SortConfig:
    """Configuration for sorting rows."""
    column: str
    ascending: bool = True
    numeric: bool = False


@dataclass
class SortResult:
    """Result of a sort operation."""
    headers: List[str]
    rows: List[List[str]]
    sort_column: str
    ascending: bool
    numeric: bool
    row_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.row_count = len(self.rows)


def _get_sort_key(row: List[str], col_index: int, numeric: bool):
    """Return a sortable key for a row cell."""
    cell = row[col_index] if col_index < len(row) else ""
    if numeric:
        try:
            return (0, float(cell.replace(",", "")))
        except (ValueError, AttributeError):
            return (1, cell.lower())
    return cell.lower()


def sort_rows(
    headers: List[str],
    rows: List[List[str]],
    config: SortConfig,
) -> SortResult:
    """Sort *rows* by the column specified in *config*.

    Rows whose sort column is missing or empty are placed at the end
    regardless of sort direction.
    """
    if config.column not in headers:
        raise ValueError(
            f"Sort column '{config.column}' not found in headers: {headers}"
        )

    col_index = headers.index(config.column)

    sorted_rows = sorted(
        rows,
        key=lambda r: _get_sort_key(r, col_index, config.numeric),
        reverse=not config.ascending,
    )

    return SortResult(
        headers=headers,
        rows=sorted_rows,
        sort_column=config.column,
        ascending=config.ascending,
        numeric=config.numeric,
    )
