"""Tests for sheetpipe.aggregator."""
import pytest
from sheetpipe.aggregator import AggregateConfig, aggregate_rows


HEADERS = ["region", "product", "revenue"]
ROWS = [
    ["north", "widget", "100"],
    ["south", "gadget", "200"],
    ["north", "gadget", "150"],
    ["south", "widget", "50"],
    ["north", "widget", "75"],
]


def _cfg(**kwargs):
    defaults = dict(group_by="region", target_column="revenue", functions=["count", "sum"])
    defaults.update(kwargs)
    return AggregateConfig(**defaults)


def test_count_and_sum():
    result = aggregate_rows(HEADERS, ROWS, _cfg())
    assert result.groups["north"]["count"] == 3.0
    assert result.groups["north"]["sum"] == 325.0
    assert result.groups["south"]["count"] == 2.0
    assert result.groups["south"]["sum"] == 250.0


def test_min_max_mean():
    result = aggregate_rows(HEADERS, ROWS, _cfg(functions=["min", "max", "mean"]))
    assert result.groups["north"]["min"] == 75.0
    assert result.groups["north"]["max"] == 150.0
    assert abs(result.groups["north"]["mean"] - (325 / 3)) < 1e-9


def test_empty_rows_returns_empty_groups():
    result = aggregate_rows(HEADERS, [], _cfg())
    assert result.groups == {}


def test_invalid_numeric_value_adds_warning():
    rows = [["north", "widget", "N/A"]]
    result = aggregate_rows(HEADERS, rows, _cfg(functions=["count", "sum"]))
    assert len(result.warnings) == 1
    assert result.groups["north"]["count"] == 0.0
    assert "sum" not in result.groups["north"]


def test_missing_group_by_raises():
    with pytest.raises(ValueError, match="group_by column"):
        aggregate_rows(HEADERS, ROWS, _cfg(group_by="nonexistent"))


def test_missing_target_column_raises():
    with pytest.raises(ValueError, match="target_column"):
        aggregate_rows(HEADERS, ROWS, _cfg(target_column="nonexistent"))


def test_unsupported_function_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        aggregate_rows(HEADERS, ROWS, _cfg(functions=["median"]))


def test_comma_separated_numbers_coerced():
    rows = [["north", "widget", "1,000"]]
    result = aggregate_rows(HEADERS, rows, _cfg(functions=["sum"]))
    assert result.groups["north"]["sum"] == 1000.0


def test_no_warnings_on_clean_data():
    result = aggregate_rows(HEADERS, ROWS, _cfg())
    assert result.warnings == []
