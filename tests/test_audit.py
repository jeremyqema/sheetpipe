"""Tests for sheetpipe.audit module."""

from __future__ import annotations

import json
import os

import pytest

from sheetpipe.audit import (
    AuditEntry,
    append_audit_log,
    make_entry,
    read_audit_log,
)


def _base_entry(**kwargs) -> AuditEntry:
    defaults = dict(
        sheet_id="sheet123",
        table_name="my_table",
        rows_fetched=100,
        rows_inserted=98,
        rows_invalid=2,
        status="success",
    )
    defaults.update(kwargs)
    return make_entry(**defaults)


def test_make_entry_fields():
    entry = _base_entry()
    assert entry.sheet_id == "sheet123"
    assert entry.table_name == "my_table"
    assert entry.rows_fetched == 100
    assert entry.rows_inserted == 98
    assert entry.rows_invalid == 2
    assert entry.status == "success"
    assert entry.error is None


def test_make_entry_timestamp_format():
    entry = _base_entry()
    # Should be a valid ISO-8601 UTC string ending with Z
    assert entry.timestamp.endswith("Z")
    assert "T" in entry.timestamp


def test_make_entry_with_error():
    entry = _base_entry(status="failure", error="connection refused")
    assert entry.status == "failure"
    assert entry.error == "connection refused"


def test_to_dict_contains_all_keys():
    entry = _base_entry()
    d = entry.to_dict()
    for key in ("timestamp", "sheet_id", "table_name", "rows_fetched",
                "rows_inserted", "rows_invalid", "status", "error"):
        assert key in d


def test_append_and_read_audit_log(tmp_path):
    log_file = str(tmp_path / "audit" / "run.log")
    entry1 = _base_entry(rows_inserted=50)
    entry2 = _base_entry(status="failure", error="timeout", rows_inserted=0)

    append_audit_log(entry1, log_file)
    append_audit_log(entry2, log_file)

    records = read_audit_log(log_file)
    assert len(records) == 2
    assert records[0]["rows_inserted"] == 50
    assert records[1]["status"] == "failure"
    assert records[1]["error"] == "timeout"


def test_read_audit_log_missing_file(tmp_path):
    result = read_audit_log(str(tmp_path / "nonexistent.log"))
    assert result == []


def test_log_lines_are_valid_json(tmp_path):
    log_file = str(tmp_path / "run.log")
    append_audit_log(_base_entry(), log_file)
    with open(log_file) as fh:
        lines = [l.strip() for l in fh if l.strip()]
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["sheet_id"] == "sheet123"
