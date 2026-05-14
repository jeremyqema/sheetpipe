"""Unit tests for sheetpipe.loader (PostgreSQL loader)."""

from unittest.mock import MagicMock, call, patch

import pytest

from sheetpipe.loader import load_to_postgres


def _make_pg_mock():
    """Return (conn_mock, cursor_mock) with context-manager support."""
    cur = MagicMock()
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cur)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cur


@patch("sheetpipe.loader.psycopg2.extras.execute_batch")
@patch("sheetpipe.loader.psycopg2.connect")
def test_load_creates_table_and_inserts(mock_connect, mock_batch):
    conn, cur = _make_pg_mock()
    mock_connect.return_value = conn

    headers = ["id", "name", "active"]
    rows = [["1", "Alice", "true"], ["2", "Bob", "false"]]

    count = load_to_postgres("dsn", "users", headers, rows)

    assert count == 2
    # CREATE TABLE should have been executed
    create_call_sql = cur.execute.call_args_list[0][0][0]
    assert "CREATE TABLE" in create_call_sql
    assert "users" in create_call_sql
    # execute_batch should have been called once
    mock_batch.assert_called_once()


@patch("sheetpipe.loader.psycopg2.extras.execute_batch")
@patch("sheetpipe.loader.psycopg2.connect")
def test_load_drop_if_exists(mock_connect, mock_batch):
    conn, cur = _make_pg_mock()
    mock_connect.return_value = conn

    load_to_postgres("dsn", "tbl", ["x"], [["1"]], drop_if_exists=True)

    drop_call_sql = cur.execute.call_args_list[0][0][0]
    assert "DROP TABLE IF EXISTS" in drop_call_sql


@patch("sheetpipe.loader.psycopg2.connect")
def test_load_empty_headers_returns_zero(mock_connect):
    count = load_to_postgres("dsn", "tbl", [], [])
    assert count == 0
    mock_connect.assert_not_called()


@patch("sheetpipe.loader.psycopg2.extras.execute_batch")
@patch("sheetpipe.loader.psycopg2.connect")
def test_load_no_rows_skips_insert(mock_connect, mock_batch):
    conn, cur = _make_pg_mock()
    mock_connect.return_value = conn

    count = load_to_postgres("dsn", "tbl", ["col1"], [])

    assert count == 0
    mock_batch.assert_not_called()
