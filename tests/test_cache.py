"""Tests for sheetpipe.cache module."""

import json
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from sheetpipe.cache import (
    _cache_key,
    _cache_path,
    read_cache,
    write_cache,
    invalidate_cache,
    DEFAULT_TTL_SECONDS,
)

SPREADSHEET_ID = "abc123"
RANGE = "Sheet1!A1:Z"
SAMPLE_ROWS = [["name", "age"], ["Alice", "30"]]


def test_cache_key_is_deterministic():
    k1 = _cache_key(SPREADSHEET_ID, RANGE)
    k2 = _cache_key(SPREADSHEET_ID, RANGE)
    assert k1 == k2
    assert len(k1) == 16


def test_cache_key_differs_for_different_inputs():
    k1 = _cache_key(SPREADSHEET_ID, RANGE)
    k2 = _cache_key(SPREADSHEET_ID, "Sheet2!A1:Z")
    assert k1 != k2


def test_write_and_read_cache(tmp_path):
    cache_dir = str(tmp_path / "cache")
    write_cache(SPREADSHEET_ID, RANGE, SAMPLE_ROWS, cache_dir=cache_dir)
    result = read_cache(SPREADSHEET_ID, RANGE, cache_dir=cache_dir)
    assert result == SAMPLE_ROWS


def test_read_cache_returns_none_when_missing(tmp_path):
    cache_dir = str(tmp_path / "cache")
    result = read_cache(SPREADSHEET_ID, RANGE, cache_dir=cache_dir)
    assert result is None


def test_read_cache_returns_none_when_expired(tmp_path):
    cache_dir = str(tmp_path / "cache")
    write_cache(SPREADSHEET_ID, RANGE, SAMPLE_ROWS, cache_dir=cache_dir)
    path = _cache_path(cache_dir, SPREADSHEET_ID, RANGE)
    # Backdate the cached_at timestamp
    with open(path, "r") as f:
        payload = json.load(f)
    old_time = (datetime.utcnow() - timedelta(seconds=600)).isoformat()
    payload["cached_at"] = old_time
    with open(path, "w") as f:
        json.dump(payload, f)
    result = read_cache(SPREADSHEET_ID, RANGE, ttl_seconds=300, cache_dir=cache_dir)
    assert result is None
    assert not os.path.exists(path)


def test_invalidate_removes_cache_file(tmp_path):
    cache_dir = str(tmp_path / "cache")
    write_cache(SPREADSHEET_ID, RANGE, SAMPLE_ROWS, cache_dir=cache_dir)
    removed = invalidate_cache(SPREADSHEET_ID, RANGE, cache_dir=cache_dir)
    assert removed is True
    assert read_cache(SPREADSHEET_ID, RANGE, cache_dir=cache_dir) is None


def test_invalidate_returns_false_when_no_file(tmp_path):
    cache_dir = str(tmp_path / "cache")
    result = invalidate_cache(SPREADSHEET_ID, RANGE, cache_dir=cache_dir)
    assert result is False
