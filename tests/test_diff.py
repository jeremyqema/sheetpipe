"""Tests for sheetpipe.diff module."""

import pytest
from sheetpipe.diff import diff_rows, DiffResult


def test_no_changes_returns_all_unchanged():
    rows = [["Alice", "30"], ["Bob", "25"]]
    result = diff_rows(rows, rows)
    assert not result.has_changes
    assert len(result.unchanged) == 2
    assert result.added == []
    assert result.removed == []


def test_all_added_when_previous_empty():
    current = [["Alice", "30"], ["Bob", "25"]]
    result = diff_rows([], current)
    assert result.has_changes
    assert len(result.added) == 2
    assert result.removed == []
    assert result.unchanged == []


def test_all_removed_when_current_empty():
    previous = [["Alice", "30"], ["Bob", "25"]]
    result = diff_rows(previous, [])
    assert result.has_changes
    assert len(result.removed) == 2
    assert result.added == []
    assert result.unchanged == []


def test_partial_change():
    previous = [["Alice", "30"], ["Bob", "25"]]
    current = [["Alice", "30"], ["Carol", "28"]]
    result = diff_rows(previous, current)
    assert result.has_changes
    assert ["Carol", "28"] in result.added
    assert ["Bob", "25"] in result.removed
    assert ["Alice", "30"] in result.unchanged


def test_duplicate_rows_handled_correctly():
    previous = [["A", "1"], ["A", "1"]]
    current = [["A", "1"]]
    result = diff_rows(previous, current)
    assert len(result.removed) == 1
    assert len(result.unchanged) == 1


def test_summary_keys_present():
    result = diff_rows([["x"]], [["y"]])
    summary = result.summary
    assert "added" in summary
    assert "removed" in summary
    assert "unchanged" in summary


def test_summary_counts_match():
    previous = [["a"], ["b"], ["c"]]
    current = [["a"], ["b"], ["d"]]
    result = diff_rows(previous, current)
    assert result.summary["added"] == 1
    assert result.summary["removed"] == 1
    assert result.summary["unchanged"] == 2


def test_empty_both_sides():
    result = diff_rows([], [])
    assert not result.has_changes
    assert result.summary == {"added": 0, "removed": 0, "unchanged": 0}
