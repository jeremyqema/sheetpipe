"""Tests for sheetpipe.enricher."""
from sheetpipe.enricher import (
    EnrichmentConfig,
    EnrichmentResult,
    enrich_rows,
    kept_count,
)


HEADERS = ["first_name", "last_name", "score"]
ROWS = [
    ["Alice", "Smith", "42"],
    ["Bob", "Jones", "17"],
]


def test_no_configs_returns_original():
    result = enrich_rows(HEADERS, ROWS, [])
    assert result.headers == HEADERS
    assert result.rows == ROWS
    assert result.enriched_columns == []


def test_single_computed_column():
    cfg = EnrichmentConfig(
        column_name="full_name",
        expression=lambda row: f"{row['first_name']} {row['last_name']}",
    )
    result = enrich_rows(HEADERS, ROWS, [cfg])
    assert "full_name" in result.headers
    assert result.rows[0][-1] == "Alice Smith"
    assert result.rows[1][-1] == "Bob Jones"


def test_multiple_enrichments_appended_in_order():
    cfgs = [
        EnrichmentConfig("full_name", lambda row: f"{row['first_name']} {row['last_name']}"),
        EnrichmentConfig("score_doubled", lambda row: str(int(row["score"]) * 2)),
    ]
    result = enrich_rows(HEADERS, ROWS, cfgs)
    assert result.headers[-2] == "full_name"
    assert result.headers[-1] == "score_doubled"
    assert result.rows[0][-1] == "84"
    assert result.rows[1][-1] == "34"


def test_expression_error_uses_default():
    cfg = EnrichmentConfig(
        column_name="bad_col",
        expression=lambda row: int(row["score"]) / 0,
        default="ERR",
    )
    result = enrich_rows(HEADERS, ROWS, [cfg])
    assert result.rows[0][-1] == "ERR"
    assert len(result.warnings) == 2


def test_expression_returns_none_uses_default():
    cfg = EnrichmentConfig(
        column_name="maybe",
        expression=lambda row: None,
        default="N/A",
    )
    result = enrich_rows(HEADERS, ROWS, [cfg])
    assert all(r[-1] == "N/A" for r in result.rows)


def test_kept_count_matches_rows():
    result = enrich_rows(HEADERS, ROWS, [])
    assert kept_count(result) == len(ROWS)


def test_empty_rows_returns_empty_result():
    cfg = EnrichmentConfig("x", lambda row: "v")
    result = enrich_rows(HEADERS, [], [cfg])
    assert result.rows == []
    assert "x" in result.headers
