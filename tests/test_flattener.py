import pytest

from sheetpipe.flattener import FlattenConfig, flatten_rows
from sheetpipe.flattener_config_loader import FlattenConfigError, load_flatten_config


HEADERS = ["id", "tags", "value"]


def _cfg(column="tags", delimiter=",", strip=True, skip=True):
    return FlattenConfig(column=column, delimiter=delimiter, strip_whitespace=strip, skip_empty_segments=skip)


# ---------------------------------------------------------------------------
# flatten_rows
# ---------------------------------------------------------------------------

def test_single_segment_row_unchanged():
    rows = [["1", "alpha", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert result.rows == [["1", "alpha", "10"]]
    assert result.output_row_count == 1
    assert result.expansion_count == 0


def test_multi_segment_expands_into_multiple_rows():
    rows = [["1", "a,b,c", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert result.output_row_count == 3
    assert [r[1] for r in result.rows] == ["a", "b", "c"]
    # Other columns preserved
    assert all(r[0] == "1" for r in result.rows)
    assert all(r[2] == "10" for r in result.rows)


def test_whitespace_stripped_by_default():
    rows = [["1", " a , b ", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert [r[1] for r in result.rows] == ["a", "b"]


def test_whitespace_not_stripped_when_disabled():
    rows = [["1", " a , b ", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg(strip=False))
    assert [r[1] for r in result.rows] == [" a ", " b "]


def test_empty_segments_skipped_by_default():
    rows = [["1", "a,,b", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert [r[1] for r in result.rows] == ["a", "b"]


def test_empty_segments_kept_when_skip_disabled():
    rows = [["1", "a,,b", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg(skip=False))
    assert len(result.rows) == 3


def test_entirely_empty_cell_produces_one_empty_row():
    rows = [["1", "", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert result.output_row_count == 1
    assert result.rows[0][1] == ""


def test_multiple_input_rows_each_expanded():
    rows = [["1", "a,b", "x"], ["2", "c", "y"]]
    result = flatten_rows(HEADERS, rows, _cfg())
    assert result.output_row_count == 3
    assert result.original_row_count == 2


def test_missing_column_returns_rows_unchanged_with_warning():
    rows = [["1", "a,b", "x"]]
    result = flatten_rows(HEADERS, rows, _cfg(column="nonexistent"))
    assert result.rows == rows
    assert len(result.warnings) == 1
    assert "nonexistent" in result.warnings[0]


def test_custom_delimiter():
    rows = [["1", "a|b|c", "10"]]
    result = flatten_rows(HEADERS, rows, _cfg(delimiter="|"))
    assert [r[1] for r in result.rows] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# load_flatten_config
# ---------------------------------------------------------------------------

def test_load_minimal_config():
    cfg = load_flatten_config({"column": "tags"})
    assert cfg.column == "tags"
    assert cfg.delimiter == ","
    assert cfg.strip_whitespace is True
    assert cfg.skip_empty_segments is True


def test_load_full_config():
    cfg = load_flatten_config(
        {"column": "items", "delimiter": ";", "strip_whitespace": False, "skip_empty": False}
    )
    assert cfg.column == "items"
    assert cfg.delimiter == ";"
    assert cfg.strip_whitespace is False
    assert cfg.skip_empty_segments is False


def test_missing_column_raises():
    with pytest.raises(FlattenConfigError, match="column"):
        load_flatten_config({"delimiter": ","})


def test_empty_column_raises():
    with pytest.raises(FlattenConfigError):
        load_flatten_config({"column": ""})


def test_empty_delimiter_raises():
    with pytest.raises(FlattenConfigError, match="delimiter"):
        load_flatten_config({"column": "tags", "delimiter": ""})
