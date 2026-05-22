"""Tests for sheetpipe.joiner."""
import pytest

from sheetpipe.joiner import JoinConfig, JoinResult, join_rows


LEFT_HEADERS = ["id", "name"]
LEFT_ROWS = [
    ["1", "Alice"],
    ["2", "Bob"],
    ["3", "Carol"],
]

RIGHT_HEADERS = ["user_id", "score"]
RIGHT_ROWS = [
    ["1", "95"],
    ["2", "80"],
    ["4", "70"],
]


def _cfg(**kwargs) -> JoinConfig:
    defaults = dict(left_key="id", right_key="user_id", join_type="inner")
    defaults.update(kwargs)
    return JoinConfig(**defaults)


def test_inner_join_returns_only_matched_rows():
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, RIGHT_ROWS, _cfg())
    assert result.headers == ["id", "name", "right_score"]
    assert len(result.rows) == 2
    keys = [r[0] for r in result.rows]
    assert "1" in keys and "2" in keys


def test_left_join_preserves_unmatched_left():
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, RIGHT_ROWS, _cfg(join_type="left"))
    assert len(result.rows) == 3
    carol = next(r for r in result.rows if r[1] == "Carol")
    assert carol[-1] == ""  # no score
    assert result.unmatched_left == 1


def test_right_join_includes_unmatched_right():
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, RIGHT_ROWS, _cfg(join_type="right"))
    row_keys = [r[0] for r in result.rows]
    assert "" in row_keys  # unmatched right row has empty left columns
    assert result.unmatched_right == 1


def test_merged_headers_use_prefix():
    cfg = _cfg(right_prefix="r_")
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, RIGHT_ROWS, cfg)
    assert "r_score" in result.headers


def test_missing_left_key_raises():
    with pytest.raises(ValueError, match="left_key"):
        join_rows(["x"], [["1"]], RIGHT_HEADERS, RIGHT_ROWS, _cfg())


def test_missing_right_key_raises():
    with pytest.raises(ValueError, match="user_id"):
        join_rows(LEFT_HEADERS, LEFT_ROWS, ["other"], [["1"]], _cfg())


def test_empty_right_dataset_inner_returns_empty():
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, [], _cfg())
    assert result.rows == []
    assert result.unmatched_left == 3


def test_empty_left_dataset_returns_empty():
    result = join_rows(LEFT_HEADERS, [], RIGHT_HEADERS, RIGHT_ROWS, _cfg())
    assert result.rows == []


def test_unmatched_left_warning_generated():
    result = join_rows(LEFT_HEADERS, LEFT_ROWS, RIGHT_HEADERS, RIGHT_ROWS, _cfg())
    assert any("unmatched" in w for w in result.warnings)
