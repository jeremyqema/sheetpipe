"""Unit tests for sheetpipe.schema — type inference logic."""

import pytest
from sheetpipe.schema import infer_pg_type, infer_schema


def test_infer_integer_column():
    assert infer_pg_type(["1", "2", "42"]) == "INTEGER"


def test_infer_float_column():
    assert infer_pg_type(["1.5", "2.0", "3.14"]) == "DOUBLE PRECISION"


def test_infer_boolean_column():
    assert infer_pg_type(["true", "false", "True"]) == "BOOLEAN"


def test_infer_text_column():
    assert infer_pg_type(["hello", "world"]) == "TEXT"


def test_infer_empty_column_defaults_to_text():
    assert infer_pg_type([]) == "TEXT"
    assert infer_pg_type([None, "", None]) == "TEXT"


def test_mixed_int_and_float_becomes_float():
    assert infer_pg_type(["1", "2.5", "3"]) == "DOUBLE PRECISION"


def test_infer_schema_returns_correct_mapping():
    headers = ["id", "name", "score", "active"]
    rows = [
        ["1", "Alice", "9.5", "true"],
        ["2", "Bob", "8.0", "false"],
    ]
    schema = infer_schema(headers, rows)
    assert schema["id"] == "INTEGER"
    assert schema["name"] == "TEXT"
    assert schema["score"] == "DOUBLE PRECISION"
    assert schema["active"] == "BOOLEAN"


def test_infer_schema_handles_short_rows():
    headers = ["a", "b", "c"]
    rows = [["1", "hello"]]
    schema = infer_schema(headers, rows)
    assert schema["c"] == "TEXT"  # missing value treated as null
