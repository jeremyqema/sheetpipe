"""Row-level diff utilities for comparing fetched data against cached snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

Row = List[str]


@dataclass
class DiffResult:
    added: List[Row] = field(default_factory=list)
    removed: List[Row] = field(default_factory=list)
    unchanged: List[Row] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)

    @property
    def summary(self) -> dict:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "unchanged": len(self.unchanged),
        }


def _row_key(row: Row) -> Tuple[str, ...]:
    """Convert a row list to a hashable tuple key."""
    return tuple(row)


def diff_rows(previous: List[Row], current: List[Row]) -> DiffResult:
    """Compare two lists of rows and return a DiffResult.

    Rows are compared by value (order-independent set semantics).
    Duplicate rows are handled via multiset counting.
    """
    from collections import Counter

    prev_counts: Counter = Counter(_row_key(r) for r in previous)
    curr_counts: Counter = Counter(_row_key(r) for r in current)

    added: List[Row] = []
    removed: List[Row] = []
    unchanged: List[Row] = []

    all_keys = set(prev_counts) | set(curr_counts)
    for key in all_keys:
        p = prev_counts.get(key, 0)
        c = curr_counts.get(key, 0)
        row = list(key)
        if c > p:
            added.extend([row] * (c - p))
            unchanged.extend([row] * p)
        elif p > c:
            removed.extend([row] * (p - c))
            unchanged.extend([row] * c)
        else:
            unchanged.extend([row] * c)

    return DiffResult(added=added, removed=removed, unchanged=unchanged)
