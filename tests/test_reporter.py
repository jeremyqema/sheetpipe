"""Tests for sheetpipe.reporter."""
import io
import json

from sheetpipe.validator import ValidationResult
from sheetpipe.reporter import report_validation


def _make_result(valid=2, invalid=None):
    result = ValidationResult()
    result.valid_rows = [[str(i)] for i in range(valid)]
    if invalid:
        for idx, reason in invalid:
            result.invalid_rows.append((idx, [], reason))
    return result


def test_text_report_no_errors():
    buf = io.StringIO()
    result = _make_result(valid=3)
    report_validation(result, table_name="sales", out=buf)
    output = buf.getvalue()
    assert "sales" in output
    assert "Valid rows  : 3" in output
    assert "Invalid rows: 0" in output
    assert "Errors" not in output


def test_text_report_with_errors():
    buf = io.StringIO()
    result = _make_result(valid=1, invalid=[(2, "empty row"), (5, "column count mismatch")])
    report_validation(result, table_name="orders", out=buf)
    output = buf.getvalue()
    assert "Invalid rows: 2" in output
    assert "row 2: empty row" in output
    assert "row 5: column count mismatch" in output


def test_json_report_structure():
    buf = io.StringIO()
    result = _make_result(valid=4, invalid=[(1, "empty row")])
    report_validation(result, table_name="users", out=buf, fmt="json")
    data = json.loads(buf.getvalue())
    assert data["table"] == "users"
    assert data["valid_rows"] == 4
    assert data["invalid_rows"] == 1
    assert data["errors"][0]["row_index"] == 1
    assert data["errors"][0]["reason"] == "empty row"


def test_json_report_no_errors():
    buf = io.StringIO()
    result = _make_result(valid=2)
    report_validation(result, out=buf, fmt="json")
    data = json.loads(buf.getvalue())
    assert data["errors"] == []
