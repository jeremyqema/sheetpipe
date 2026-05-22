"""Pivot rows by grouping on a key column and spreading a value column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PivotConfig:
    row_key_column: str          # column whose values become row identifiers
    pivot_column: str            # column whose distinct values become new headers
    value_column: str            # column supplying cell values
    fill_value: str = ""         # value used when a combination is absent
    sort_pivot_headers: bool = True


@dataclass
class PivotResult:
    headers: List[str]
    rows: List[List[str]]
    pivot_values: List[str]      # the distinct values that became new columns
    warnings: List[str] = field(default_factory=list)


def _col_index(headers: List[str], name: str) -> Optional[int]:
    try:
        return headers.index(name)
    except ValueError:
        return None


def pivot_rows(
    headers: List[str],
    rows: List[List[str]],
    config: PivotConfig,
) -> PivotResult:
    """Pivot *rows* according to *config*.

    The original *row_key_column* and *pivot_column* are consumed; all other
    columns are treated as pass-through and must have a consistent value per
    *row_key_column* (the first seen value wins).
    """
    warnings: List[str] = []

    key_idx = _col_index(headers, config.row_key_column)
    pivot_idx = _col_index(headers, config.pivot_column)
    value_idx = _col_index(headers, config.value_column)

    missing = [
        name for name, idx in [
            (config.row_key_column, key_idx),
            (config.pivot_column, pivot_idx),
            (config.value_column, value_idx),
        ] if idx is None
    ]
    if missing:
        raise ValueError(f"Pivot columns not found in headers: {missing}")

    passthrough_indices = [
        i for i, h in enumerate(headers)
        if i not in (key_idx, pivot_idx, value_idx)
    ]
    passthrough_headers = [headers[i] for i in passthrough_indices]

    # Collect distinct pivot values and row ordering
    pivot_values_seen: dict[str, None] = {}
    row_order: list[str] = []
    # key -> pivot_val -> cell_value
    data: dict[str, dict[str, str]] = {}
    # key -> passthrough values (first seen)
    passthrough_data: dict[str, list[str]] = {}

    for row in rows:
        key = row[key_idx] if key_idx < len(row) else ""
        pval = row[pivot_idx] if pivot_idx < len(row) else ""
        val = row[value_idx] if value_idx < len(row) else ""

        pivot_values_seen.setdefault(pval, None)
        if key not in data:
            data[key] = {}
            row_order.append(key)
            passthrough_data[key] = [
                row[i] if i < len(row) else "" for i in passthrough_indices
            ]
        if pval in data[key]:
            warnings.append(
                f"Duplicate pivot key='{key}' pivot_val='{pval}'; keeping first value."
            )
        else:
            data[key][pval] = val

    pivot_values = list(pivot_values_seen)
    if config.sort_pivot_headers:
        pivot_values = sorted(pivot_values)

    out_headers = [config.row_key_column] + passthrough_headers + pivot_values
    out_rows: List[List[str]] = []
    for key in row_order:
        pt = passthrough_data[key]
        cells = [data[key].get(pv, config.fill_value) for pv in pivot_values]
        out_rows.append([key] + pt + cells)

    return PivotResult(
        headers=out_headers,
        rows=out_rows,
        pivot_values=pivot_values,
        warnings=warnings,
    )
