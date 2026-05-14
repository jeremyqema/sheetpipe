"""Top-level pipeline orchestration for sheetpipe."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from sheetpipe.fetcher import fetch_sheet_data
from sheetpipe.schema import infer_schema
from sheetpipe.ddl import sanitize_identifier
from sheetpipe.validator import validate_rows
from sheetpipe.transformer import transform_rows
from sheetpipe.loader import load_to_postgres
from sheetpipe.reporter import report_validation

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    spreadsheet_id: str
    sheet_range: str
    pg_dsn: str
    table_name: Optional[str] = None
    drop_if_exists: bool = False
    drop_invalid_rows: bool = True
    report_format: str = "text"  # "text" | "json"
    credentials_file: Optional[str] = None
    extra_options: dict = field(default_factory=dict)


def resolved_table_name(config: PipelineConfig) -> str:
    """Return an explicit table name or derive one from the sheet range."""
    if config.table_name:
        return sanitize_identifier(config.table_name)
    base = config.sheet_range.split("!")[0]
    return sanitize_identifier(base)


def run_pipeline(config: PipelineConfig) -> dict:
    """Execute the full extract-validate-transform-load pipeline.

    Returns a summary dict with keys: table, rows_loaded, validation_errors.
    """
    logger.info("Fetching sheet data from %s (%s)", config.spreadsheet_id, config.sheet_range)
    headers, raw_rows = fetch_sheet_data(
        config.spreadsheet_id,
        config.sheet_range,
        credentials_file=config.credentials_file,
    )

    if not headers:
        logger.warning("Sheet returned no headers — aborting pipeline.")
        return {"table": None, "rows_loaded": 0, "validation_errors": 0}

    # Sanitize headers so they match what the DDL layer will produce
    clean_headers = [sanitize_identifier(h) for h in headers]

    # Infer schema from raw rows (strings)
    schema = infer_schema(clean_headers, raw_rows)

    # Validate
    validation_result = validate_rows(
        raw_rows,
        expected_columns=len(clean_headers),
        drop_invalid=config.drop_invalid_rows,
    )
    report = report_validation(validation_result, fmt=config.report_format)
    logger.info("Validation report:\n%s", report)

    valid_rows = validation_result.valid_rows

    # Transform
    typed_rows = transform_rows(valid_rows, clean_headers, schema)

    # Load
    table = resolved_table_name(config)
    rows_loaded = load_to_postgres(
        dsn=config.pg_dsn,
        table=table,
        headers=clean_headers,
        schema=schema,
        rows=typed_rows,
        drop_if_exists=config.drop_if_exists,
    )

    logger.info("Loaded %d rows into '%s'.", rows_loaded, table)
    return {
        "table": table,
        "rows_loaded": rows_loaded,
        "validation_errors": validation_result.error_count,
    }
