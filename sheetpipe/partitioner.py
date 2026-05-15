"""Row partitioning utilities for sheetpipe.

Splits a list of rows into named partitions based on a column value,
enabling per-partition table loading or reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PartitionConfig:
    column: str
    default_partition: str = "__default__"
    lowercase_keys: bool = True


@dataclass
class PartitionResult:
    partitions: Dict[str, List[List[str]]] = field(default_factory=dict)
    headers: List[str] = field(default_factory=list)
    unmatched_count: int = 0


def _get_partition_key(row: List[str], col_index: int, config: PartitionConfig) -> str:
    """Return the partition key for a row, falling back to default."""
    if col_index < 0 or col_index >= len(row):
        return config.default_partition
    value = row[col_index].strip()
    if not value:
        return config.default_partition
    return value.lower() if config.lowercase_keys else value


def partition_rows(
    headers: List[str],
    rows: List[List[str]],
    config: PartitionConfig,
) -> PartitionResult:
    """Partition rows by the value found in config.column.

    Args:
        headers: Column header names.
        rows: Data rows (list of lists).
        config: Partitioning configuration.

    Returns:
        PartitionResult with one entry per distinct partition key.
    """
    result = PartitionResult(headers=list(headers))

    try:
        col_index = headers.index(config.column)
    except ValueError:
        col_index = -1
        result.unmatched_count = len(rows)

    for row in rows:
        key = _get_partition_key(row, col_index, config)
        if key == config.default_partition:
            result.unmatched_count += 1
        result.partitions.setdefault(key, []).append(row)

    return result


def partition_names(result: PartitionResult) -> List[str]:
    """Return sorted list of partition names."""
    return sorted(result.partitions.keys())
