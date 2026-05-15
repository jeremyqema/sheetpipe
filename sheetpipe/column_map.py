"""Column mapping: rename and reorder sheet columns before loading."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ColumnMapConfig:
    """Defines how to rename and/or reorder columns."""
    rename: Dict[str, str] = field(default_factory=dict)   # original -> new name
    order: List[str] = field(default_factory=list)          # desired final order (original names)
    drop: List[str] = field(default_factory=list)           # original names to drop


@dataclass
class ColumnMapResult:
    headers: List[str]
    rows: List[List[str]]
    dropped_columns: List[str]


def apply_column_map(
    headers: List[str],
    rows: List[List[str]],
    config: ColumnMapConfig,
) -> ColumnMapResult:
    """Apply rename, drop, and reorder operations to headers and rows."""
    # Determine which columns to keep and their indices
    kept_originals = [h for h in headers if h not in config.drop]
    dropped_columns = [h for h in headers if h in config.drop]

    # Build the ordered list of original names
    if config.order:
        # Only include columns that are in kept_originals, preserving requested order
        ordered = [h for h in config.order if h in kept_originals]
        # Append any kept columns not mentioned in order (stable, left-to-right)
        mentioned = set(config.order)
        for h in kept_originals:
            if h not in mentioned:
                ordered.append(h)
    else:
        ordered = list(kept_originals)

    # Build index map: original_name -> position in original headers
    index_of = {h: i for i, h in enumerate(headers)}

    # Produce renamed headers
    new_headers = [config.rename.get(orig, orig) for orig in ordered]

    # Remap rows
    new_rows: List[List[str]] = []
    for row in rows:
        new_row: List[Optional[str]] = []
        for orig in ordered:
            idx = index_of.get(orig)
            if idx is not None and idx < len(row):
                new_row.append(row[idx])
            else:
                new_row.append("")
        new_rows.append(new_row)

    return ColumnMapResult(
        headers=new_headers,
        rows=new_rows,
        dropped_columns=dropped_columns,
    )
