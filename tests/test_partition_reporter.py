"""Tests for sheetpipe.partition_reporter."""

import io
import json

import pytest

from sheetpipe.partitioner import PartitionResult, partition_rows, PartitionConfig
from sheetpipe.partition_reporter import (
    format_text_partition_report,
    format_json_partition_report,
    report_partitions,
)

HEADERS = ["region", "item", "qty"]
ROWS = [
    ["north", "a", "1"],
    ["south", "b", "2"],
    ["north", "c", "3"],
]


def _result():
    return partition_rows(HEADERS, ROWS, PartitionConfig(column="region"))


def test_text_report_contains_partition_names():
    text = format_text_partition_report(_result())
    assert "north" in text
    assert "south" in text


def test_text_report_shows_row_counts():
    text = format_text_partition_report(_result())
    assert "2 row(s)" in text  # north has 2
    assert "1 row(s)" in text  # south has 1


def test_text_report_shows_total():
    text = format_text_partition_report(_result())
    assert "Total: 3 row(s)" in text


def test_json_report_structure():
    raw = format_json_partition_report(_result())
    data = json.loads(raw)
    assert "partitions" in data
    assert "total_rows" in data
    assert "unmatched_count" in data
    assert "partition_count" in data


def test_json_report_values():
    raw = format_json_partition_report(_result())
    data = json.loads(raw)
    assert data["total_rows"] == 3
    assert data["partition_count"] == 2
    assert data["partitions"]["north"] == 2
    assert data["partitions"]["south"] == 1


def test_report_partitions_writes_to_stream_text():
    buf = io.StringIO()
    report_partitions(_result(), fmt="text", stream=buf)
    assert "north" in buf.getvalue()


def test_report_partitions_writes_to_stream_json():
    buf = io.StringIO()
    report_partitions(_result(), fmt="json", stream=buf)
    data = json.loads(buf.getvalue())
    assert data["total_rows"] == 3


def test_report_partitions_returns_string():
    buf = io.StringIO()
    result = report_partitions(_result(), fmt="text", stream=buf)
    assert isinstance(result, str)
    assert len(result) > 0
