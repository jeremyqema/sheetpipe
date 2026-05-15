"""Tests for sheetpipe.column_map and sheetpipe.column_map_loader."""
import pytest

from sheetpipe.column_map import ColumnMapConfig, apply_column_map
from sheetpipe.column_map_loader import ColumnMapConfigError, load_column_map_config

HEADERS = ["id", "First Name", "Last Name", "score", "notes"]
ROWS = [
    ["1", "Alice", "Smith", "95", "good"],
    ["2", "Bob", "Jones", "80", ""],
]


def test_no_op_config_preserves_headers_and_rows():
    cfg = ColumnMapConfig()
    result = apply_column_map(HEADERS, ROWS, cfg)
    assert result.headers == HEADERS
    assert result.rows == ROWS
    assert result.dropped_columns == []


def test_rename_single_column():
    cfg = ColumnMapConfig(rename={"First Name": "first_name", "Last Name": "last_name"})
    result = apply_column_map(HEADERS, ROWS, cfg)
    assert "first_name" in result.headers
    assert "last_name" in result.headers
    assert "First Name" not in result.headers


def test_drop_column_removes_it():
    cfg = ColumnMapConfig(drop=["notes"])
    result = apply_column_map(HEADERS, ROWS, cfg)
    assert "notes" not in result.headers
    assert result.dropped_columns == ["notes"]
    assert all(len(r) == 4 for r in result.rows)


def test_order_reorders_columns():
    cfg = ColumnMapConfig(order=["score", "id"])
    result = apply_column_map(HEADERS, ROWS, cfg)
    assert result.headers[0] == "score"
    assert result.headers[1] == "id"
    # remaining columns appended in original order
    assert set(result.headers) == set(HEADERS)


def test_order_with_drop():
    cfg = ColumnMapConfig(order=["id", "score"], drop=["notes", "Last Name"])
    result = apply_column_map(HEADERS, ROWS, cfg)
    assert "notes" not in result.headers
    assert "Last Name" not in result.headers
    assert result.headers[0] == "id"
    assert result.headers[1] == "score"


def test_row_values_follow_reorder():
    cfg = ColumnMapConfig(order=["score", "id"])
    result = apply_column_map(HEADERS, ROWS, cfg)
    score_idx = result.headers.index("score")
    id_idx = result.headers.index("id")
    assert result.rows[0][score_idx] == "95"
    assert result.rows[0][id_idx] == "1"


def test_short_row_padded_with_empty_string():
    short_rows = [["1", "Alice"]]  # missing last 3 columns
    cfg = ColumnMapConfig()
    result = apply_column_map(HEADERS, short_rows, cfg)
    assert len(result.rows[0]) == len(HEADERS)
    assert result.rows[0][2] == ""


# --- loader tests ---

def test_load_column_map_config_full():
    raw = {"rename": {"First Name": "first_name"}, "order": ["id"], "drop": ["notes"]}
    cfg = load_column_map_config(raw)
    assert cfg.rename == {"First Name": "first_name"}
    assert cfg.order == ["id"]
    assert cfg.drop == ["notes"]


def test_load_column_map_config_empty_dict():
    cfg = load_column_map_config({})
    assert cfg.rename == {}
    assert cfg.order == []
    assert cfg.drop == []


def test_load_column_map_config_bad_rename_raises():
    with pytest.raises(ColumnMapConfigError, match="rename"):
        load_column_map_config({"rename": ["not", "a", "dict"]})


def test_load_column_map_config_bad_order_raises():
    with pytest.raises(ColumnMapConfigError, match="order"):
        load_column_map_config({"order": "col_a"})


def test_load_column_map_config_bad_drop_raises():
    with pytest.raises(ColumnMapConfigError, match="drop"):
        load_column_map_config({"drop": 42})


def test_load_column_map_config_non_string_rename_value_raises():
    with pytest.raises(ColumnMapConfigError):
        load_column_map_config({"rename": {"col": 123}})
