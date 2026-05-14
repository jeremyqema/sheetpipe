"""Tests for the CLI module."""

from unittest.mock import MagicMock, patch

import pytest

from sheetpipe.cli import build_parser, main


def test_parser_required_args():
    parser = build_parser()
    args = parser.parse_args(["SHEET_ID", "Sheet1!A1:Z", "postgresql://localhost/db"])
    assert args.spreadsheet_id == "SHEET_ID"
    assert args.sheet_range == "Sheet1!A1:Z"
    assert args.dsn == "postgresql://localhost/db"


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["ID", "Range", "dsn"])
    assert args.table is None
    assert args.drop is False
    assert args.keep_invalid is False
    assert args.report_format == "text"
    assert args.credentials is None


def test_parser_optional_flags():
    parser = build_parser()
    args = parser.parse_args([
        "ID", "Range", "dsn",
        "--table", "my_table",
        "--drop",
        "--keep-invalid",
        "--report-format", "json",
        "--credentials", "/path/to/creds.json",
    ])
    assert args.table == "my_table"
    assert args.drop is True
    assert args.keep_invalid is True
    assert args.report_format == "json"
    assert args.credentials == "/path/to/creds.json"


def test_main_success_returns_zero():
    mock_result = {"report": "All good", "rows_loaded": 5}
    with patch("sheetpipe.cli.run_pipeline", return_value=mock_result) as mock_run:
        code = main(["ID", "Sheet1!A1:Z", "postgresql://localhost/db"])
    assert code == 0
    mock_run.assert_called_once()


def test_main_pipeline_exception_returns_one(capsys):
    with patch("sheetpipe.cli.run_pipeline", side_effect=RuntimeError("boom")):
        code = main(["ID", "Sheet1!A1:Z", "dsn"])
    assert code == 1
    captured = capsys.readouterr()
    assert "boom" in captured.err


def test_main_passes_config_correctly():
    mock_result = {"report": "", "rows_loaded": 0}
    with patch("sheetpipe.cli.run_pipeline", return_value=mock_result) as mock_run:
        main(["MY_ID", "Sheet1!A:Z", "postgresql://host/db", "--drop", "--table", "tbl"])
    config = mock_run.call_args[0][0]
    assert config.spreadsheet_id == "MY_ID"
    assert config.drop_if_exists is True
    assert config.table_name == "tbl"
