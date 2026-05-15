"""Tests for sheetpipe.partitioner."""

import pytest

from sheetpipe.partitioner import (
    PartitionConfig,
    PartitionResult,
    partition_rows,
    partition_names,
)

HEADERS = ["region", "product", "sales"]

ROWS = [
    ["north", "widget", "100"],
    ["south", "gadget", "200"],
    ["north", "gizmo", "150"],
    ["east", "widget", "80"],
    ["south", "widget", "60"],
]


def _cfg(column="region", **kwargs):
    return PartitionConfig(column=column, **kwargs)


def test_partition_groups_by_column():
    result = partition_rows(HEADERS, ROWS, _cfg())
    assert set(result.partitions.keys()) == {"north", "south", "east"}
    assert len(result.partitions["north"]) == 2
    assert len(result.partitions["south"]) == 2
    assert len(result.partitions["east"]) == 1


def test_partition_preserves_headers():
    result = partition_rows(HEADERS, ROWS, _cfg())
    assert result.headers == HEADERS


def test_partition_lowercase_keys():
    rows = [["North", "x", "1"], ["NORTH", "y", "2"]]
    result = partition_rows(HEADERS, rows, _cfg(lowercase_keys=True))
    assert "north" in result.partitions
    assert len(result.partitions["north"]) == 2


def test_partition_no_lowercase():
    rows = [["North", "x", "1"], ["NORTH", "y", "2"]]
    result = partition_rows(HEADERS, rows, _cfg(lowercase_keys=False))
    assert "North" in result.partitions
    assert "NORTH" in result.partitions


def test_partition_missing_column_sends_to_default():
    result = partition_rows(HEADERS, ROWS, _cfg(column="nonexistent"))
    assert result.unmatched_count == len(ROWS)
    assert "__default__" in result.partitions


def test_partition_empty_value_goes_to_default():
    rows = [["north", "a", "1"], ["", "b", "2"]]
    result = partition_rows(HEADERS, rows, _cfg())
    assert result.unmatched_count == 1
    assert "__default__" in result.partitions


def test_partition_empty_rows():
    result = partition_rows(HEADERS, [], _cfg())
    assert result.partitions == {}
    assert result.unmatched_count == 0


def test_partition_names_sorted():
    result = partition_rows(HEADERS, ROWS, _cfg())
    assert partition_names(result) == sorted({"north", "south", "east"})


def test_custom_default_partition_name():
    rows = [["", "x", "1"]]
    result = partition_rows(HEADERS, rows, _cfg(default_partition="other"))
    assert "other" in result.partitions
