"""Tests for sheetpipe.transformer."""

import pytest
from sheetpipe.transformer import coerce_value, transform_row, transform_rows


# ---------------------------------------------------------------------------
# coerce_value
# ---------------------------------------------------------------------------

def test_coerce_integer_valid():
    assert coerce_value("42", "INTEGER") == 42


def test_coerce_integer_with_comma():
    assert coerce_value("1,000", "INTEGER") == 1000


def test_coerce_integer_invalid_returns_none():
    assert coerce_value("abc", "INTEGER") is None


def test_coerce_numeric_valid():
    assert coerce_value("3.14", "NUMERIC") == pytest.approx(3.14)


def test_coerce_boolean_true_variants():
    for v in ("true", "True", "yes", "YES", "1"):
        assert coerce_value(v, "BOOLEAN") is True, f"Expected True for {v!r}"


def test_coerce_boolean_false_variants():
    for v in ("false", "False", "no", "NO", "0"):
        assert coerce_value(v, "BOOLEAN") is False, f"Expected False for {v!r}"


def test_coerce_boolean_invalid_returns_none():
    assert coerce_value("maybe", "BOOLEAN") is None


def test_coerce_text_passthrough():
    assert coerce_value("  hello world  ", "TEXT") == "hello world"


def test_coerce_empty_string_returns_none():
    for pg_type in ("INTEGER", "NUMERIC", "BOOLEAN", "TEXT"):
        assert coerce_value("", pg_type) is None
        assert coerce_value("   ", pg_type) is None


# ---------------------------------------------------------------------------
# transform_row
# ---------------------------------------------------------------------------

def test_transform_row_basic():
    headers = ["age", "score", "active", "name"]
    schema = {"age": "INTEGER", "score": "NUMERIC", "active": "BOOLEAN", "name": "TEXT"}
    row = ["30", "9.5", "true", "Alice"]
    result = transform_row(row, headers, schema)
    assert result == {"age": 30, "score": pytest.approx(9.5), "active": True, "name": "Alice"}


def test_transform_row_short_row_fills_none():
    headers = ["a", "b", "c"]
    schema = {"a": "INTEGER", "b": "TEXT", "c": "TEXT"}
    result = transform_row(["1"], headers, schema)
    assert result["a"] == 1
    assert result["b"] is None
    assert result["c"] is None


# ---------------------------------------------------------------------------
# transform_rows
# ---------------------------------------------------------------------------

def test_transform_rows_returns_list_of_dicts():
    headers = ["id", "label"]
    schema = {"id": "INTEGER", "label": "TEXT"}
    rows = [["1", "foo"], ["2", "bar"]]
    results = transform_rows(rows, headers, schema)
    assert len(results) == 2
    assert results[0] == {"id": 1, "label": "foo"}
    assert results[1] == {"id": 2, "label": "bar"}


def test_transform_rows_empty_input():
    assert transform_rows([], ["x"], {"x": "TEXT"}) == []
