"""Tests for sheetpipe/truncator.py."""
import pytest

from sheetpipe.truncator import (
    TruncateConfig,
    TruncateResult,
    kept_count,
    truncate_rows,
)

HEADERS = ["id", "name", "value"]
ROWS = [
    ["1", "alpha", "10"],
    ["2", "beta", "20"],
    ["3", "gamma", "30"],
    ["4", "delta", "40"],
    ["5", "epsilon", "50"],
]


def test_no_config_returns_all_rows():
    result = truncate_rows(HEADERS, ROWS)
    assert result.rows == ROWS
    assert result.total_before == 5
    assert result.dropped_count == 0
    assert kept_count(result) == 5


def test_limit_reduces_rows():
    cfg = TruncateConfig(limit=3)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.rows == ROWS[:3]
    assert result.dropped_count == 2
    assert kept_count(result) == 3


def test_limit_larger_than_rows_keeps_all():
    cfg = TruncateConfig(limit=100)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.rows == ROWS
    assert result.dropped_count == 0


def test_offset_skips_leading_rows():
    cfg = TruncateConfig(limit=2, offset=2)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.rows == ROWS[2:4]
    assert result.total_before == 5
    assert result.dropped_count == 3


def test_offset_beyond_rows_returns_empty_with_warning():
    cfg = TruncateConfig(limit=3, offset=10)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.rows == []
    assert result.dropped_count == 5
    assert len(result.warnings) == 1
    assert "offset" in result.warnings[0]


def test_limit_zero_returns_empty():
    cfg = TruncateConfig(limit=0)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.rows == []
    assert result.dropped_count == 5


def test_headers_preserved():
    cfg = TruncateConfig(limit=2)
    result = truncate_rows(HEADERS, ROWS, cfg)
    assert result.headers == HEADERS


def test_negative_limit_raises():
    with pytest.raises(ValueError, match="limit"):
        TruncateConfig(limit=-1)


def test_negative_offset_raises():
    with pytest.raises(ValueError, match="offset"):
        TruncateConfig(limit=5, offset=-3)


def test_empty_rows_with_config():
    cfg = TruncateConfig(limit=10, offset=0)
    result = truncate_rows(HEADERS, [], cfg)
    assert result.rows == []
    assert result.total_before == 0
    assert result.dropped_count == 0
