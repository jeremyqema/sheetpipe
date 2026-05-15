"""Tests for sheetpipe.filter_config_loader module."""
import pytest
from sheetpipe.filter_config_loader import load_filter_configs, FilterConfigError
from sheetpipe.filter import FilterConfig


def test_load_single_valid_filter():
    raw = [{"column": "status", "operator": "eq", "value": "active"}]
    configs = load_filter_configs(raw)
    assert len(configs) == 1
    assert configs[0].column == "status"
    assert configs[0].operator == "eq"
    assert configs[0].value == "active"
    assert configs[0].case_sensitive is True


def test_load_multiple_filters():
    raw = [
        {"column": "age", "operator": "gte", "value": 18},
        {"column": "city", "operator": "contains", "value": "York", "case_sensitive": False},
    ]
    configs = load_filter_configs(raw)
    assert len(configs) == 2
    assert configs[1].case_sensitive is False


def test_empty_list_returns_empty():
    assert load_filter_configs([]) == []


def test_missing_column_raises():
    with pytest.raises(FilterConfigError, match="missing required key 'column'"):
        load_filter_configs([{"operator": "eq", "value": "x"}])


def test_missing_operator_raises():
    with pytest.raises(FilterConfigError, match="missing required key 'operator'"):
        load_filter_configs([{"column": "x", "value": "y"}])


def test_missing_value_raises():
    with pytest.raises(FilterConfigError, match="missing required key 'value'"):
        load_filter_configs([{"column": "x", "operator": "eq"}])


def test_invalid_operator_raises():
    with pytest.raises(FilterConfigError, match="unknown operator 'regex'"):
        load_filter_configs([{"column": "x", "operator": "regex", "value": ".*"}])


def test_non_list_input_raises():
    with pytest.raises(FilterConfigError, match="filters must be a list"):
        load_filter_configs({"column": "x", "operator": "eq", "value": "y"})  # type: ignore


def test_all_valid_operators_accepted():
    operators = ["eq", "neq", "gt", "lt", "gte", "lte", "contains", "startswith"]
    raw = [{"column": "col", "operator": op, "value": "1"} for op in operators]
    configs = load_filter_configs(raw)
    assert len(configs) == len(operators)


def test_case_sensitive_defaults_to_true():
    raw = [{"column": "name", "operator": "eq", "value": "Alice"}]
    config = load_filter_configs(raw)[0]
    assert config.case_sensitive is True
