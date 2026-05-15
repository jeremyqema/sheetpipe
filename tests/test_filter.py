"""Tests for sheetpipe.filter module."""
import pytest
from sheetpipe.filter import FilterConfig, FilterResult, apply_filters, _get_cell, _matches

HEADERS = ["name", "age", "city"]
ROWS = [
    ["Alice", "30", "New York"],
    ["Bob", "25", "Boston"],
    ["Carol", "35", "New York"],
    ["Dave", "17", "Chicago"],
]


def test_no_filters_keeps_all_rows():
    result = apply_filters(HEADERS, ROWS, [])
    assert result.kept == ROWS
    assert result.dropped == []
    assert result.kept_count == 4
    assert result.dropped_count == 0


def test_eq_filter():
    filters = [FilterConfig(column="city", operator="eq", value="New York")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 2
    assert all(r[2] == "New York" for r in result.kept)


def test_neq_filter():
    filters = [FilterConfig(column="city", operator="neq", value="New York")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 2
    assert all(r[2] != "New York" for r in result.kept)


def test_gt_filter():
    filters = [FilterConfig(column="age", operator="gt", value="20")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 3


def test_lte_filter():
    filters = [FilterConfig(column="age", operator="lte", value="25")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 2


def test_contains_filter():
    filters = [FilterConfig(column="city", operator="contains", value="New")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 2


def test_startswith_filter():
    filters = [FilterConfig(column="name", operator="startswith", value="A")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 1
    assert result.kept[0][0] == "Alice"


def test_case_insensitive_filter():
    filters = [FilterConfig(column="city", operator="eq", value="new york", case_sensitive=False)]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 2


def test_multiple_filters_combined():
    filters = [
        FilterConfig(column="city", operator="eq", value="New York"),
        FilterConfig(column="age", operator="gte", value="35"),
    ]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 1
    assert result.kept[0][0] == "Carol"


def test_unknown_column_drops_all():
    filters = [FilterConfig(column="missing", operator="eq", value="x")]
    result = apply_filters(HEADERS, ROWS, filters)
    assert result.kept_count == 0
    assert result.dropped_count == 4


def test_get_cell_returns_none_for_short_row():
    assert _get_cell(["Alice"], HEADERS, "city") is None


def test_matches_non_numeric_comparison_returns_false():
    assert _matches("hello", "gt", "world", True) is False
