"""Tests for sheetpipe.validator."""
import pytest

from sheetpipe.validator import validate_rows, ValidationResult


HEADERS = ["id", "name", "score"]


def test_all_valid_rows():
    rows = [["1", "Alice", "9.5"], ["2", "Bob", "8.0"]]
    result = validate_rows(HEADERS, rows)
    assert result.valid_rows == rows
    assert result.error_count == 0
    assert not result.has_errors


def test_empty_row_is_invalid():
    rows = [["1", "Alice", "9.5"], ["", "", ""]]
    result = validate_rows(HEADERS, rows)
    assert len(result.valid_rows) == 1
    assert result.error_count == 1
    assert "empty row" in result.invalid_rows[0][2]


def test_short_row_is_invalid_and_dropped_by_default():
    rows = [["1", "Alice"], ["2", "Bob", "8.0"]]
    result = validate_rows(HEADERS, rows)
    assert len(result.valid_rows) == 1
    assert result.error_count == 1
    assert "column count mismatch" in result.invalid_rows[0][2]


def test_short_row_kept_when_drop_invalid_false():
    rows = [["1", "Alice"]]
    result = validate_rows(HEADERS, rows, drop_invalid=False)
    assert len(result.valid_rows) == 1
    assert result.error_count == 1


def test_long_row_is_invalid():
    rows = [["1", "Alice", "9.5", "extra"]]
    result = validate_rows(HEADERS, rows)
    assert result.error_count == 1
    assert result.valid_rows == []


def test_empty_input():
    result = validate_rows(HEADERS, [])
    assert result.valid_rows == []
    assert result.error_count == 0


def test_invalid_row_index_recorded():
    rows = [["1", "Alice", "9.5"], ["", None, ""]]
    result = validate_rows(HEADERS, rows)
    bad_idx, bad_row, reason = result.invalid_rows[0]
    assert bad_idx == 1
    assert reason == "empty row"
