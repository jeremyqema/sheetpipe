"""Reporting utilities for partition results."""

from __future__ import annotations

import json
from typing import IO, Optional

from sheetpipe.partitioner import PartitionResult, partition_names


def format_text_partition_report(result: PartitionResult) -> str:
    """Return a human-readable summary of partition counts."""
    lines = ["Partition Summary", "-" * 30]
    for name in partition_names(result):
        count = len(result.partitions[name])
        lines.append(f"  {name}: {count} row(s)")
    if result.unmatched_count:
        lines.append(f"  [unmatched/default]: {result.unmatched_count} row(s)")
    total = sum(len(v) for v in result.partitions.values())
    lines.append("-" * 30)
    lines.append(f"  Total: {total} row(s) across {len(result.partitions)} partition(s)")
    return "\n".join(lines)


def format_json_partition_report(result: PartitionResult) -> str:
    """Return a JSON-encoded partition summary."""
    payload = {
        "partitions": {
            name: len(rows) for name, rows in result.partitions.items()
        },
        "unmatched_count": result.unmatched_count,
        "total_rows": sum(len(v) for v in result.partitions.values()),
        "partition_count": len(result.partitions),
    }
    return json.dumps(payload, indent=2)


def report_partitions(
    result: PartitionResult,
    fmt: str = "text",
    stream: Optional[IO[str]] = None,
) -> str:
    """Print and return a partition report.

    Args:
        result: The PartitionResult to report on.
        fmt: ``"text"`` or ``"json"``.
        stream: Output stream; defaults to stdout via print.

    Returns:
        The formatted report string.
    """
    import sys

    output = stream or sys.stdout

    if fmt == "json":
        text = format_json_partition_report(result)
    else:
        text = format_text_partition_report(result)

    print(text, file=output)
    return text
