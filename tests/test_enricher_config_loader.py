"""Tests for sheetpipe.enricher_config_loader."""
import pytest

from sheetpipe.enricher_config_loader import (
    EnricherConfigError,
    load_enricher_configs,
)


def test_empty_list_returns_empty():
    assert load_enricher_configs([]) == []


def test_load_single_valid_config():
    raw = [{"column_name": "upper_name", "expression": "row['name'].upper()"}]
    configs = load_enricher_configs(raw)
    assert len(configs) == 1
    assert configs[0].column_name == "upper_name"
    result = configs[0].expression({"name": "alice"})
    assert result == "ALICE"


def test_load_multiple_configs():
    raw = [
        {"column_name": "a", "expression": "'static'"},
        {"column_name": "b", "expression": "row['x'] + row['y']"},
    ]
    configs = load_enricher_configs(raw)
    assert len(configs) == 2
    assert configs[0].column_name == "a"
    assert configs[1].column_name == "b"


def test_default_is_stored():
    raw = [{"column_name": "c", "expression": "'v'", "default": "fallback"}]
    configs = load_enricher_configs(raw)
    assert configs[0].default == "fallback"


def test_missing_column_name_raises():
    with pytest.raises(EnricherConfigError, match="column_name"):
        load_enricher_configs([{"expression": "'x'"}])


def test_missing_expression_raises():
    with pytest.raises(EnricherConfigError, match="expression"):
        load_enricher_configs([{"column_name": "col"}])


def test_invalid_expression_syntax_raises():
    with pytest.raises(EnricherConfigError, match="Invalid expression"):
        load_enricher_configs([{"column_name": "col", "expression": "def bad(:"}])


def test_expression_callable_with_row():
    raw = [{"column_name": "combo", "expression": "row['a'] + '-' + row['b']"}]
    configs = load_enricher_configs(raw)
    assert configs[0].expression({"a": "foo", "b": "bar"}) == "foo-bar"
