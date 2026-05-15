"""Tests for sheetpipe.snapshot."""

import pytest

from sheetpipe.snapshot import (
    Snapshot,
    _compute_checksum,
    make_snapshot,
    snapshot_from_dict,
    snapshot_to_dict,
    snapshots_differ,
)

HEADERS = ["id", "name", "value"]
ROWS = [["1", "alpha", "10"], ["2", "beta", "20"]]


def test_make_snapshot_fields():
    snap = make_snapshot("sheet123", "Sheet1", HEADERS, ROWS)
    assert snap.sheet_id == "sheet123"
    assert snap.tab_name == "Sheet1"
    assert snap.row_count == 2
    assert snap.column_count == 3
    assert snap.headers == HEADERS
    assert len(snap.checksum) == 64  # SHA-256 hex


def test_checksum_is_deterministic():
    c1 = _compute_checksum(HEADERS, ROWS)
    c2 = _compute_checksum(HEADERS, ROWS)
    assert c1 == c2


def test_checksum_differs_on_row_change():
    c1 = _compute_checksum(HEADERS, ROWS)
    c2 = _compute_checksum(HEADERS, ROWS + [["3", "gamma", "30"]])
    assert c1 != c2


def test_checksum_differs_on_header_change():
    c1 = _compute_checksum(HEADERS, ROWS)
    c2 = _compute_checksum(["id", "label", "value"], ROWS)
    assert c1 != c2


def test_snapshots_differ_no_previous():
    snap = make_snapshot("s", "t", HEADERS, ROWS)
    assert snapshots_differ(None, snap) is True


def test_snapshots_differ_same_data():
    snap1 = make_snapshot("s", "t", HEADERS, ROWS)
    snap2 = make_snapshot("s", "t", HEADERS, ROWS)
    assert snapshots_differ(snap1, snap2) is False


def test_snapshots_differ_changed_data():
    snap1 = make_snapshot("s", "t", HEADERS, ROWS)
    snap2 = make_snapshot("s", "t", HEADERS, ROWS + [["3", "gamma", "30"]])
    assert snapshots_differ(snap1, snap2) is True


def test_snapshot_roundtrip_via_dict():
    original = make_snapshot("sheet_abc", "Data", HEADERS, ROWS)
    restored = snapshot_from_dict(snapshot_to_dict(original))
    assert restored.sheet_id == original.sheet_id
    assert restored.tab_name == original.tab_name
    assert restored.row_count == original.row_count
    assert restored.column_count == original.column_count
    assert restored.checksum == original.checksum
    assert restored.headers == original.headers


def test_snapshot_to_dict_keys():
    snap = make_snapshot("x", "y", HEADERS, ROWS)
    d = snapshot_to_dict(snap)
    assert set(d.keys()) == {"sheet_id", "tab_name", "row_count", "column_count", "checksum", "headers"}
