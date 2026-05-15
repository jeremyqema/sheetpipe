"""Tests for sheetpipe.sorter."""
import pytest

from sheetpipe.sorter import SortConfig, sort_rows


HEADERS = ["name", "age", "score"]

ROWS = [
    ["Charlie", "30", "88.5"],
    ["Alice", "25", "95.0"],
    ["Bob", "25", "72.3"],
    ["Diana", "35", "88.5"],
]


def test_sort_text_ascending():
    cfg = SortConfig(column="name", ascending=True)
    result = sort_rows(HEADERS, ROWS, cfg)
    names = [r[0] for r in result.rows]
    assert names == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_text_descending():
    cfg = SortConfig(column="name", ascending=False)
    result = sort_rows(HEADERS, ROWS, cfg)
    names = [r[0] for r in result.rows]
    assert names == ["Diana", "Charlie", "Bob", "Alice"]


def test_sort_numeric_ascending():
    cfg = SortConfig(column="score", ascending=True, numeric=True)
    result = sort_rows(HEADERS, ROWS, cfg)
    scores = [r[2] for r in result.rows]
    assert scores == ["72.3", "88.5", "88.5", "95.0"]


def test_sort_numeric_descending():
    cfg = SortConfig(column="age", ascending=False, numeric=True)
    result = sort_rows(HEADERS, ROWS, cfg)
    ages = [r[1] for r in result.rows]
    assert ages[0] == "35"
    assert ages[-1] == "25"


def test_sort_preserves_headers():
    cfg = SortConfig(column="name")
    result = sort_rows(HEADERS, ROWS, cfg)
    assert result.headers == HEADERS


def test_sort_row_count_matches():
    cfg = SortConfig(column="name")
    result = sort_rows(HEADERS, ROWS, cfg)
    assert result.row_count == len(ROWS)


def test_sort_result_metadata():
    cfg = SortConfig(column="score", ascending=False, numeric=True)
    result = sort_rows(HEADERS, ROWS, cfg)
    assert result.sort_column == "score"
    assert result.ascending is False
    assert result.numeric is True


def test_sort_invalid_column_raises():
    cfg = SortConfig(column="nonexistent")
    with pytest.raises(ValueError, match="nonexistent"):
        sort_rows(HEADERS, ROWS, cfg)


def test_sort_empty_rows():
    cfg = SortConfig(column="name")
    result = sort_rows(HEADERS, [], cfg)
    assert result.rows == []
    assert result.row_count == 0


def test_sort_short_rows_placed_last():
    rows = [["Zara", "22", "80.0"], ["Ann"]]
    cfg = SortConfig(column="score", ascending=True, numeric=True)
    result = sort_rows(HEADERS, rows, cfg)
    # "Ann" row has no score cell — should sort after numeric entries
    assert result.rows[-1][0] == "Ann"


def test_sort_numeric_with_comma_formatted_numbers():
    rows = [["A", "1", "1,200"], ["B", "2", "300"], ["C", "3", "50"]]
    cfg = SortConfig(column="score", ascending=True, numeric=True)
    result = sort_rows(HEADERS, rows, cfg)
    scores = [r[2] for r in result.rows]
    assert scores == ["50", "300", "1,200"]
