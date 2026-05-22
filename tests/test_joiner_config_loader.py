"""Tests for sheetpipe.joiner_config_loader."""
import pytest

from sheetpipe.joiner_config_loader import JoinConfigError, load_join_config


def test_minimal_valid_config():
    cfg = load_join_config({"left_key": "id", "right_key": "user_id"})
    assert cfg.left_key == "id"
    assert cfg.right_key == "user_id"
    assert cfg.join_type == "inner"
    assert cfg.right_prefix == "right_"


def test_explicit_join_type_left():
    cfg = load_join_config({"left_key": "id", "right_key": "uid", "join_type": "left"})
    assert cfg.join_type == "left"


def test_explicit_join_type_right():
    cfg = load_join_config({"left_key": "id", "right_key": "uid", "join_type": "right"})
    assert cfg.join_type == "right"


def test_custom_prefix_stored():
    cfg = load_join_config({"left_key": "a", "right_key": "b", "right_prefix": "ext_"})
    assert cfg.right_prefix == "ext_"


def test_missing_left_key_raises():
    with pytest.raises(JoinConfigError, match="left_key"):
        load_join_config({"right_key": "uid"})


def test_missing_right_key_raises():
    with pytest.raises(JoinConfigError, match="right_key"):
        load_join_config({"left_key": "id"})


def test_invalid_join_type_raises():
    with pytest.raises(JoinConfigError, match="join_type"):
        load_join_config({"left_key": "id", "right_key": "uid", "join_type": "outer"})


def test_non_dict_input_raises():
    with pytest.raises(JoinConfigError, match="mapping"):
        load_join_config(["left_key", "id"])  # type: ignore


def test_empty_left_key_raises():
    with pytest.raises(JoinConfigError, match="left_key"):
        load_join_config({"left_key": "", "right_key": "uid"})


def test_non_string_prefix_raises():
    with pytest.raises(JoinConfigError, match="right_prefix"):
        load_join_config({"left_key": "id", "right_key": "uid", "right_prefix": 42})  # type: ignore
