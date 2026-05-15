"""Load partitioned rows into separate PostgreSQL tables."""

from __future__ import annotations

from typing import Dict, List, Optional

from sheetpipe.ddl import sanitize_identifier
from sheetpipe.loader import load_to_postgres
from sheetpipe.partitioner import PartitionResult, partition_names


def _table_for_partition(
    base_table: str,
    partition_key: str,
    default_partition: str = "__default__",
) -> str:
    """Derive a table name from the base name and partition key."""
    if partition_key == default_partition:
        suffix = "default"
    else:
        suffix = sanitize_identifier(partition_key)
    base = sanitize_identifier(base_table)
    return f"{base}_{suffix}"


def load_partitions(
    result: PartitionResult,
    dsn: str,
    base_table: str,
    drop_if_exists: bool = False,
    default_partition: str = "__default__",
) -> Dict[str, int]:
    """Load each partition into its own PostgreSQL table.

    Args:
        result: PartitionResult produced by partition_rows.
        dsn: PostgreSQL connection string.
        base_table: Base name; each partition appends its key as suffix.
        drop_if_exists: Whether to drop tables before creating.
        default_partition: The key used for unmatched rows.

    Returns:
        Mapping of partition key -> number of rows inserted.
    """
    counts: Dict[str, int] = {}

    for key in partition_names(result):
        rows = result.partitions[key]
        table = _table_for_partition(base_table, key, default_partition)
        inserted = load_to_postgres(
            headers=result.headers,
            rows=rows,
            dsn=dsn,
            table_name=table,
            drop_if_exists=drop_if_exists,
        )
        counts[key] = inserted

    return counts
