"""Tests for sheetpipe.deduplicator."""
import pytest
from sheetpipe.deduplicator import (
    DeduplicateResult,
    deduplicate_rows,
    dropped_count,
    kept_count,
)

HEADERS = ["id", "name", "value"]


def test_no_duplicates_returns_all_rows():
    rows = [["1", "alice", "10"], ["2", "bob", "20"]]
    result = deduplicate_rows(HEADERS, rows)
    assert result.rows == rows
    assert dropped_count(result) == 0
    assert kept_count(result) == 2


def test_full_row_dedup_removes_exact_duplicates():
    rows = [["1", "alice", "10"], ["1", "alice", "10"], ["2", "bob", "20"]]
    result = deduplicate_rows(HEADERS, rows)
    assert kept_count(result) == 2
    assert dropped_count(result) == 1


def test_key_column_dedup_uses_only_specified_columns():
    rows = [["1", "alice", "10"], ["1", "alice", "99"], ["2", "bob", "20"]]
    result = deduplicate_rows(HEADERS, rows, key_columns=["id"])
    assert kept_count(result) == 2
    assert dropped_count(result) == 1
    assert result.rows[0] == ["1", "alice", "10"]  # first kept


def test_keep_last_retains_last_occurrence():
    rows = [["1", "alice", "10"], ["1", "alice", "99"], ["2", "bob", "20"]]
    result = deduplicate_rows(HEADERS, rows, key_columns=["id"], keep="last")
    assert kept_count(result) == 2
    assert result.rows[0] == ["1", "alice", "99"]  # last kept


def test_empty_rows_returns_empty_result():
    result = deduplicate_rows(HEADERS, [])
    assert result.rows == []
    assert dropped_count(result) == 0


def test_all_duplicates_leaves_one_row():
    rows = [["1", "a", "x"]] * 5
    result = deduplicate_rows(HEADERS, rows)
    assert kept_count(result) == 1
    assert dropped_count(result) == 4


def test_invalid_keep_value_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate_rows(HEADERS, [], keep="middle")


def test_multi_column_key():
    rows = [
        ["1", "alice", "10"],
        ["1", "alice", "20"],
        ["1", "bob", "10"],
    ]
    result = deduplicate_rows(HEADERS, rows, key_columns=["id", "name"])
    assert kept_count(result) == 2
    assert dropped_count(result) == 1
