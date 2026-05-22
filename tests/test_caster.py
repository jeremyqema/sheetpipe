"""Tests for sheetpipe.caster."""
import pytest
from sheetpipe.caster import CastConfig, CastResult, cast_rows, _cast_value


HEADERS = ["name", "age", "score", "active"]


def _rows(*tuples):
    return [list(t) for t in tuples]


# --- _cast_value unit tests ---

def test_cast_integer_valid():
    val, warn = _cast_value("42", "integer", strict=False)
    assert val == 42 and warn is None


def test_cast_integer_with_comma():
    val, warn = _cast_value("1,234", "bigint", strict=False)
    assert val == 1234 and warn is None


def test_cast_float_valid():
    val, warn = _cast_value("3.14", "numeric", strict=False)
    assert abs(val - 3.14) < 1e-9 and warn is None


def test_cast_boolean_true_variants():
    for raw in ("true", "yes", "1", "t", "y", "True", "YES"):
        val, warn = _cast_value(raw, "boolean", strict=False)
        assert val is True, f"Expected True for {raw!r}"


def test_cast_boolean_false_variants():
    for raw in ("false", "no", "0", "f", "n"):
        val, warn = _cast_value(raw, "boolean", strict=False)
        assert val is False


def test_cast_boolean_invalid_non_strict_returns_none_with_warning():
    val, warn = _cast_value("maybe", "boolean", strict=False)
    assert val is None
    assert warn is not None and "boolean" in warn


def test_cast_boolean_invalid_strict_raises():
    with pytest.raises(ValueError):
        _cast_value("maybe", "boolean", strict=True)


def test_cast_text_passthrough():
    val, warn = _cast_value("hello", "text", strict=False)
    assert val == "hello" and warn is None


def test_cast_unknown_type_passthrough():
    val, warn = _cast_value("anything", "jsonb", strict=False)
    assert val == "anything" and warn is None


# --- cast_rows integration tests ---

def test_no_column_types_returns_rows_unchanged():
    rows = _rows(("Alice", "30", "9.5", "true"))
    result = cast_rows(HEADERS, rows, CastConfig())
    assert result.rows == rows
    assert result.cast_count == 0


def test_cast_integer_column():
    rows = _rows(("Alice", "30", "9.5", "true"))
    cfg = CastConfig(column_types={"age": "integer"})
    result = cast_rows(HEADERS, rows, cfg)
    assert result.rows[0][1] == 30
    assert result.cast_count == 1


def test_cast_multiple_columns():
    rows = _rows(("Alice", "30", "9.5", "yes"), ("Bob", "25", "7.0", "no"))
    cfg = CastConfig(column_types={"age": "integer", "score": "numeric", "active": "boolean"})
    result = cast_rows(HEADERS, rows, cfg)
    assert result.rows[0] == ["Alice", 30, 9.5, True]
    assert result.rows[1] == ["Bob", 25, 7.0, False]
    assert result.cast_count == 6


def test_cast_failure_non_strict_inserts_none_and_warns():
    rows = _rows(("Alice", "not-a-number", "9.5", "true"))
    cfg = CastConfig(column_types={"age": "integer"}, strict=False)
    result = cast_rows(HEADERS, rows, cfg)
    assert result.rows[0][1] is None
    assert len(result.warnings) == 1
    assert "not-a-number" in result.warnings[0]


def test_unknown_column_in_config_produces_warning():
    rows = _rows(("Alice", "30", "9.5", "true"))
    cfg = CastConfig(column_types={"nonexistent": "integer"})
    result = cast_rows(HEADERS, rows, cfg)
    assert any("nonexistent" in w for w in result.warnings)


def test_empty_rows_returns_empty_result():
    cfg = CastConfig(column_types={"age": "integer"})
    result = cast_rows(HEADERS, [], cfg)
    assert result.rows == []
    assert result.cast_count == 0
