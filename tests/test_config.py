"""Tests for environment-based configuration loading."""

import pytest

from sheetpipe.config import EnvConfig, _parse_bool, load_env_config


def test_parse_bool_true_variants():
    for val in ("1", "true", "True", "TRUE", "yes", "YES"):
        assert _parse_bool(val) is True


def test_parse_bool_false_variants():
    for val in ("0", "false", "False", "no", "", "random"):
        assert _parse_bool(val) is False


def test_load_env_config_success(monkeypatch):
    monkeypatch.setenv("SHEETPIPE_SPREADSHEET_ID", "abc123")
    monkeypatch.setenv("SHEETPIPE_SHEET_RANGE", "Sheet1!A1:Z")
    monkeypatch.setenv("SHEETPIPE_DSN", "postgresql://localhost/test")

    config = load_env_config()
    assert config.spreadsheet_id == "abc123"
    assert config.sheet_range == "Sheet1!A1:Z"
    assert config.dsn == "postgresql://localhost/test"
    assert config.table_name is None
    assert config.drop_if_exists is False
    assert config.drop_invalid_rows is True
    assert config.report_format == "text"
    assert config.credentials_path is None


def test_load_env_config_optional_vars(monkeypatch):
    monkeypatch.setenv("SHEETPIPE_SPREADSHEET_ID", "id")
    monkeypatch.setenv("SHEETPIPE_SHEET_RANGE", "range")
    monkeypatch.setenv("SHEETPIPE_DSN", "dsn")
    monkeypatch.setenv("SHEETPIPE_TABLE_NAME", "my_table")
    monkeypatch.setenv("SHEETPIPE_DROP_IF_EXISTS", "true")
    monkeypatch.setenv("SHEETPIPE_DROP_INVALID_ROWS", "false")
    monkeypatch.setenv("SHEETPIPE_REPORT_FORMAT", "json")
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/creds.json")

    config = load_env_config()
    assert config.table_name == "my_table"
    assert config.drop_if_exists is True
    assert config.drop_invalid_rows is False
    assert config.report_format == "json"
    assert config.credentials_path == "/creds.json"


def test_load_env_config_missing_required(monkeypatch):
    monkeypatch.delenv("SHEETPIPE_SPREADSHEET_ID", raising=False)
    monkeypatch.delenv("SHEETPIPE_SHEET_RANGE", raising=False)
    monkeypatch.delenv("SHEETPIPE_DSN", raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        load_env_config()
    assert "SHEETPIPE_SPREADSHEET_ID" in str(exc_info.value)


def test_load_env_config_partial_missing(monkeypatch):
    monkeypatch.setenv("SHEETPIPE_SPREADSHEET_ID", "id")
    monkeypatch.delenv("SHEETPIPE_SHEET_RANGE", raising=False)
    monkeypatch.delenv("SHEETPIPE_DSN", raising=False)

    with pytest.raises(EnvironmentError) as exc_info:
        load_env_config()
    assert "SHEETPIPE_SHEET_RANGE" in str(exc_info.value)
    assert "SHEETPIPE_DSN" in str(exc_info.value)
