"""Row filtering utilities for sheetpipe pipelines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class FilterConfig:
    """Configuration for row-level filtering."""
    column: str
    operator: str  # eq, neq, gt, lt, gte, lte, contains, startswith
    value: Any
    case_sensitive: bool = True


@dataclass
class FilterResult:
    """Result of applying filters to a set of rows."""
    kept: List[List[Any]] = field(default_factory=list)
    dropped: List[List[Any]] = field(default_factory=list)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def dropped_count(self) -> int:
        return len(self.dropped)


def _get_cell(row: List[Any], headers: List[str], column: str) -> Optional[str]:
    """Return the cell value for a given column name."""
    try:
        idx = headers.index(column)
        return str(row[idx]) if idx < len(row) else None
    except ValueError:
        return None


def _matches(cell: Optional[str], operator: str, value: Any, case_sensitive: bool) -> bool:
    """Evaluate a single filter condition."""
    if cell is None:
        return False
    cv = str(value)
    c, v = (cell, cv) if case_sensitive else (cell.lower(), cv.lower())
    if operator == "eq":
        return c == v
    if operator == "neq":
        return c != v
    if operator == "contains":
        return v in c
    if operator == "startswith":
        return c.startswith(v)
    try:
        fc, fv = float(c), float(v)
    except (ValueError, TypeError):
        return False
    if operator == "gt":
        return fc > fv
    if operator == "lt":
        return fc < fv
    if operator == "gte":
        return fc >= fv
    if operator == "lte":
        return fc <= fv
    return False


def apply_filters(
    headers: List[str],
    rows: List[List[Any]],
    filters: List[FilterConfig],
) -> FilterResult:
    """Apply all filters to rows; a row is kept only if it passes every filter."""
    result = FilterResult()
    for row in rows:
        if all(
            _matches(_get_cell(row, headers, f.column), f.operator, f.value, f.case_sensitive)
            for f in filters
        ):
            result.kept.append(row)
        else:
            result.dropped.append(row)
    return result
