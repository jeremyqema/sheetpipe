"""Row aggregation utilities for sheetpipe.

Supports grouping rows by a column and computing aggregate functions
(count, sum, min, max, mean) over a numeric target column.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AggregateConfig:
    group_by: str
    target_column: str
    functions: List[str] = field(default_factory=lambda: ["count"])


@dataclass
class AggregateResult:
    config: AggregateConfig
    groups: Dict[str, Dict[str, float]]
    warnings: List[str] = field(default_factory=list)


_SUPPORTED = {"count", "sum", "min", "max", "mean"}


def _get_cell(row: List[str], headers: List[str], col: str) -> Optional[str]:
    try:
        idx = headers.index(col)
        return row[idx] if idx < len(row) else None
    except ValueError:
        return None


def _compute_entry(vals: List[float], functions: List[str]) -> Dict[str, float]:
    """Compute requested aggregate functions over *vals*.

    Always computes ``count`` regardless of available values; other functions
    are only computed when at least one numeric value is present.
    """
    entry: Dict[str, float] = {}
    n = len(vals)
    if "count" in functions:
        entry["count"] = float(n)
    if n > 0:
        if "sum" in functions:
            entry["sum"] = sum(vals)
        if "min" in functions:
            entry["min"] = min(vals)
        if "max" in functions:
            entry["max"] = max(vals)
        if "mean" in functions:
            entry["mean"] = sum(vals) / n
    return entry


def aggregate_rows(
    headers: List[str],
    rows: List[List[str]],
    config: AggregateConfig,
) -> AggregateResult:
    """Group rows by *config.group_by* and compute aggregate functions."""
    warnings: List[str] = []
    unknown = [f for f in config.functions if f not in _SUPPORTED]
    if unknown:
        raise ValueError(f"Unsupported aggregate functions: {unknown}")

    if config.group_by not in headers:
        raise ValueError(f"group_by column '{config.group_by}' not in headers")
    if config.target_column not in headers:
        raise ValueError(f"target_column '{config.target_column}' not in headers")

    buckets: Dict[str, List[float]] = {}
    for row in rows:
        key = _get_cell(row, headers, config.group_by) or ""
        raw = _get_cell(row, headers, config.target_column)
        try:
            val = float(raw.replace(",", "")) if raw else None
        except (ValueError, AttributeError):
            warnings.append(f"Cannot convert '{raw}' to float; skipping.")
            val = None
        buckets.setdefault(key, [])
        if val is not None:
            buckets[key].append(val)

    groups: Dict[str, Dict[str, float]] = {
        key: _compute_entry(vals, config.functions)
        for key, vals in buckets.items()
    }

    return AggregateResult(config=config, groups=groups, warnings=warnings)
