"""Unit tests for sheetpipe.fetcher (Google Sheets data fetcher)."""

from unittest.mock import MagicMock, patch

import pytest

from sheetpipe.fetcher import fetch_sheet_data


def _make_service_mock(values: list):
    """Build a layered mock that mimics the Sheets API client."""
    execute_mock = MagicMock(return_value={"values": values})
    get_mock = MagicMock(return_value=MagicMock(execute=execute_mock))
    values_mock = MagicMock(return_value=MagicMock(get=get_mock))
    spreadsheets_mock = MagicMock(return_value=MagicMock(values=values_mock))
    service = MagicMock()
    service.spreadsheets = spreadsheets_mock
    return service


@patch("sheetpipe.fetcher._build_service")
def test_fetch_returns_headers_and_rows(mock_build):
    mock_build.return_value = _make_service_mock(
        [["id", "name", "score"], ["1", "Alice", "9.5"], ["2", "Bob", "8.0"]]
    )
    headers, rows = fetch_sheet_data("sheet_id", "Sheet1")
    assert headers == ["id", "name", "score"]
    assert rows == [["1", "Alice", "9.5"], ["2", "Bob", "8.0"]]


@patch("sheetpipe.fetcher._build_service")
def test_fetch_empty_sheet(mock_build):
    mock_build.return_value = _make_service_mock([])
    headers, rows = fetch_sheet_data("sheet_id", "EmptySheet")
    assert headers == []
    assert rows == []


@patch("sheetpipe.fetcher._build_service")
def test_fetch_pads_short_rows(mock_build):
    mock_build.return_value = _make_service_mock(
        [["a", "b", "c"], ["1", "2"], ["3"]]
    )
    headers, rows = fetch_sheet_data("sheet_id", "Sheet1")
    assert rows[0] == ["1", "2", ""]
    assert rows[1] == ["3", "", ""]


@patch("sheetpipe.fetcher._build_service")
def test_fetch_header_only_sheet(mock_build):
    mock_build.return_value = _make_service_mock([["col1", "col2"]])
    headers, rows = fetch_sheet_data("sheet_id", "Sheet1")
    assert headers == ["col1", "col2"]
    assert rows == []


def test_build_service_raises_without_credentials():
    import os
    env_backup = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    try:
        with pytest.raises(ValueError, match="Credentials path"):
            from sheetpipe.fetcher import _build_service
            _build_service()
    finally:
        if env_backup is not None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env_backup
