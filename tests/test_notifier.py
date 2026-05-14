"""Tests for sheetpipe.notifier."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from sheetpipe.audit import AuditEntry
from sheetpipe.notifier import (
    NotifierConfig,
    _format_message,
    notify,
    notify_stdout,
    notify_webhook,
)


def _entry(error: str | None = None) -> AuditEntry:
    return AuditEntry(
        timestamp="2024-01-01T00:00:00Z",
        table_name="sales",
        sheet_id="abc123",
        rows_fetched=10,
        rows_inserted=9,
        duration_seconds=1.5,
        error=error,
    )


def test_format_message_success():
    msg = _format_message(_entry())
    assert "✅" in msg
    assert "sales" in msg
    assert "rows_fetched=10" in msg
    assert "rows_inserted=9" in msg
    assert "1.50s" in msg


def test_format_message_with_error():
    msg = _format_message(_entry(error="timeout"))
    assert "❌" in msg
    assert "error=timeout" in msg


def test_notify_stdout_prints(capsys):
    notify_stdout(_entry(), NotifierConfig())
    captured = capsys.readouterr()
    assert "sales" in captured.out


def test_notify_stdout_silent_suppresses(capsys):
    notify_stdout(_entry(), NotifierConfig(silent=True))
    captured = capsys.readouterr()
    assert captured.out == ""


def test_notify_webhook_no_url_returns_false():
    result = notify_webhook(_entry(), NotifierConfig())
    assert result is False


def test_notify_webhook_success():
    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        result = notify_webhook(_entry(), NotifierConfig(webhook_url="http://hook"))
    assert result is True
    call_args = mock_open.call_args
    req = call_args[0][0]
    body = json.loads(req.data)
    assert body["table"] == "sales"
    assert body["rows_inserted"] == 9


def test_notify_webhook_network_error_returns_false():
    with patch("urllib.request.urlopen", side_effect=OSError("refused")):
        result = notify_webhook(_entry(), NotifierConfig(webhook_url="http://hook"))
    assert result is False


def test_notify_calls_both_channels(capsys):
    with patch("sheetpipe.notifier.notify_webhook", return_value=True) as mock_wh:
        notify(_entry(), NotifierConfig(webhook_url="http://hook"))
    captured = capsys.readouterr()
    assert "sales" in captured.out
    mock_wh.assert_called_once()
