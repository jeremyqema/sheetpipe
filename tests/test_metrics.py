"""Tests for sheetpipe.metrics module."""

from __future__ import annotations

import time

import pytest

from sheetpipe.metrics import PipelineMetrics, merge_metrics


# ---------------------------------------------------------------------------
# PipelineMetrics defaults
# ---------------------------------------------------------------------------

def test_default_metrics_are_zero():
    m = PipelineMetrics()
    assert m.rows_fetched == 0
    assert m.rows_valid == 0
    assert m.rows_invalid == 0
    assert m.rows_inserted == 0
    assert m.validation_errors == 0
    assert m.retries == 0
    assert m.duration_seconds == 0.0


def test_to_dict_contains_all_keys():
    m = PipelineMetrics(rows_fetched=10, rows_inserted=8)
    d = m.to_dict()
    expected_keys = {
        "rows_fetched", "rows_valid", "rows_invalid",
        "rows_inserted", "validation_errors", "retries", "duration_seconds",
    }
    assert expected_keys.issubset(d.keys())


def test_to_dict_values_match_fields():
    m = PipelineMetrics(rows_fetched=5, rows_valid=4, rows_invalid=1, rows_inserted=4)
    d = m.to_dict()
    assert d["rows_fetched"] == 5
    assert d["rows_valid"] == 4
    assert d["rows_invalid"] == 1
    assert d["rows_inserted"] == 4


def test_to_dict_includes_extra_fields():
    m = PipelineMetrics(extra={"sheet_id": "abc123", "table": "my_table"})
    d = m.to_dict()
    assert d["sheet_id"] == "abc123"
    assert d["table"] == "my_table"


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------

def test_timer_records_elapsed_duration():
    m = PipelineMetrics()
    m.start_timer()
    time.sleep(0.05)
    m.stop_timer()
    assert m.duration_seconds >= 0.04
    assert m.duration_seconds < 1.0


def test_stop_timer_without_start_does_not_raise():
    m = PipelineMetrics()
    m.stop_timer()  # should be a no-op
    assert m.duration_seconds == 0.0


def test_duration_rounded_in_to_dict():
    m = PipelineMetrics(duration_seconds=1.23456789)
    d = m.to_dict()
    assert d["duration_seconds"] == round(1.23456789, 4)


# ---------------------------------------------------------------------------
# merge_metrics
# ---------------------------------------------------------------------------

def test_merge_sums_numeric_fields():
    a = PipelineMetrics(rows_fetched=10, rows_inserted=8, retries=1)
    b = PipelineMetrics(rows_fetched=5, rows_inserted=5, retries=2)
    merged = merge_metrics(a, b)
    assert merged.rows_fetched == 15
    assert merged.rows_inserted == 13
    assert merged.retries == 3


def test_merge_combines_extra_dicts():
    a = PipelineMetrics(extra={"key_a": 1})
    b = PipelineMetrics(extra={"key_b": 2})
    merged = merge_metrics(a, b)
    assert merged.extra["key_a"] == 1
    assert merged.extra["key_b"] == 2


def test_merge_does_not_mutate_originals():
    a = PipelineMetrics(rows_fetched=3)
    b = PipelineMetrics(rows_fetched=7)
    merge_metrics(a, b)
    assert a.rows_fetched == 3
    assert b.rows_fetched == 7
