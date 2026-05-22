"""Tests for sheetpipe.pivot."""
import pytest
from sheetpipe.pivot import PivotConfig, PivotResult, pivot_rows


HEADERS = ["region", "quarter", "revenue"]
ROWS = [
    ["north", "Q1", "100"],
    ["north", "Q2", "200"],
    ["south", "Q1", "150"],
    ["south", "Q2", "250"],
]


def _cfg(**kwargs) -> PivotConfig:
    defaults = dict(
        row_key_column="region",
        pivot_column="quarter",
        value_column="revenue",
    )
    defaults.update(kwargs)
    return PivotConfig(**defaults)


def test_pivot_basic_structure():
    result = pivot_rows(HEADERS, ROWS, _cfg())
    assert isinstance(result, PivotResult)
    assert result.headers == ["region", "Q1", "Q2"]
    assert result.pivot_values == ["Q1", "Q2"]


def test_pivot_row_values():
    result = pivot_rows(HEADERS, ROWS, _cfg())
    rows_by_key = {r[0]: r for r in result.rows}
    assert rows_by_key["north"] == ["north", "100", "200"]
    assert rows_by_key["south"] == ["150", "250"] or rows_by_key["south"][1:] == ["150", "250"]


def test_pivot_preserves_row_order():
    result = pivot_rows(HEADERS, ROWS, _cfg())
    assert [r[0] for r in result.rows] == ["north", "south"]


def test_pivot_sorted_headers():
    rows = [
        ["a", "Z", "1"],
        ["a", "A", "2"],
    ]
    result = pivot_rows(["key", "cat", "val"], rows, PivotConfig("key", "cat", "val"))
    assert result.pivot_values == ["A", "Z"]


def test_pivot_unsorted_headers():
    rows = [["a", "Z", "1"], ["a", "A", "2"]]
    cfg = PivotConfig("key", "cat", "val", sort_pivot_headers=False)
    result = pivot_rows(["key", "cat", "val"], rows, cfg)
    assert result.pivot_values == ["Z", "A"]


def test_pivot_fill_value_for_missing_combinations():
    rows = [
        ["north", "Q1", "100"],
        ["south", "Q2", "250"],
    ]
    result = pivot_rows(HEADERS, ROWS[:0] + rows, _cfg(fill_value="0"))
    rows_by_key = {r[0]: r for r in result.rows}
    assert rows_by_key["north"][-1] == "0"   # Q2 missing for north
    assert rows_by_key["south"][1] == "0"    # Q1 missing for south


def test_pivot_passthrough_columns():
    headers = ["region", "manager", "quarter", "revenue"]
    rows = [
        ["north", "Alice", "Q1", "100"],
        ["north", "Alice", "Q2", "200"],
    ]
    result = pivot_rows(headers, rows, PivotConfig("region", "quarter", "revenue"))
    assert "manager" in result.headers
    assert result.rows[0][result.headers.index("manager")] == "Alice"


def test_pivot_duplicate_emits_warning():
    rows = [
        ["north", "Q1", "100"],
        ["north", "Q1", "999"],  # duplicate
    ]
    result = pivot_rows(HEADERS, rows, _cfg())
    assert len(result.warnings) == 1
    assert "Q1" in result.warnings[0]
    # First value should be kept
    assert result.rows[0][result.headers.index("Q1")] == "100"


def test_pivot_missing_column_raises():
    with pytest.raises(ValueError, match="not found in headers"):
        pivot_rows(HEADERS, ROWS, PivotConfig("region", "MISSING", "revenue"))


def test_pivot_empty_rows_returns_empty():
    result = pivot_rows(HEADERS, [], _cfg())
    assert result.rows == []
    assert result.pivot_values == []
