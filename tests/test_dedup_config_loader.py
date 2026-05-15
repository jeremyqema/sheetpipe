"""Tests for sheetpipe.dedup_config_loader."""
import pytest
from sheetpipe.dedup_config_loader import DedupConfigError, load_dedup_config


def test_empty_dict_returns_defaults():
    key_columns, keep = load_dedup_config({})
    assert key_columns is None
    assert keep == "first"


def test_explicit_key_columns_parsed():
    key_columns, keep = load_dedup_config({"key_columns": ["id", "date"]})
    assert key_columns == ["id", "date"]
    assert keep == "first"


def test_keep_last_parsed():
    key_columns, keep = load_dedup_config({"keep": "last"})
    assert keep == "last"
    assert key_columns is None


def test_full_config_parsed():
    key_columns, keep = load_dedup_config({"key_columns": ["id"], "keep": "last"})
    assert key_columns == ["id"]
    assert keep == "last"


def test_invalid_keep_raises():
    with pytest.raises(DedupConfigError, match="keep"):
        load_dedup_config({"keep": "none"})


def test_key_columns_not_a_list_raises():
    with pytest.raises(DedupConfigError, match="key_columns"):
        load_dedup_config({"key_columns": "id"})


def test_empty_key_columns_raises():
    with pytest.raises(DedupConfigError, match="must not be empty"):
        load_dedup_config({"key_columns": []})


def test_key_columns_with_non_string_raises():
    with pytest.raises(DedupConfigError, match="list of strings"):
        load_dedup_config({"key_columns": ["id", 42]})


def test_non_dict_input_raises():
    with pytest.raises(DedupConfigError, match="must be a dict"):
        load_dedup_config(["id", "keep"])  # type: ignore
