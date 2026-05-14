"""Unit tests for sheetpipe.ddl — DDL generation utilities."""

import pytest
from sheetpipe.ddl import sanitize_identifier, build_create_table, build_insert


def test_sanitize_simple():
    assert sanitize_identifier("Name") == "name"


def test_sanitize_spaces_and_special_chars():
    assert sanitize_identifier("First Name!") == "first_name"


def test_sanitize_leading_digit():
    assert sanitize_identifier("1value") == "col_1value"


def test_sanitize_multiple_underscores():
    assert sanitize_identifier("foo__bar") == "foo_bar"


def test_build_create_table_basic():
    schema = {"id": "INTEGER", "name": "TEXT"}
    ddl = build_create_table("users", schema)
    assert "CREATE TABLE IF NOT EXISTS users" in ddl
    assert "id INTEGER" in ddl
    assert "name TEXT" in ddl


def test_build_create_table_without_if_not_exists():
    schema = {"id": "INTEGER"}
    ddl = build_create_table("users", schema, if_not_exists=False)
    assert "IF NOT EXISTS" not in ddl
    assert "CREATE TABLE users" in ddl


def test_build_create_table_sanitizes_names():
    schema = {"User ID": "INTEGER", "Full Name": "TEXT"}
    ddl = build_create_table("My Table", schema)
    assert "my_table" in ddl
    assert "user_id" in ddl
    assert "full_name" in ddl


def test_build_insert_basic():
    sql = build_insert("users", ["id", "name"])
    assert "INSERT INTO users" in sql
    assert "%(id)s" in sql
    assert "%(name)s" in sql


def test_build_insert_sanitizes_headers():
    sql = build_insert("orders", ["Order ID", "Total Price"])
    assert "order_id" in sql
    assert "total_price" in sql
