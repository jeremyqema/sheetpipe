"""Top-level pipeline orchestrator for sheetpipe."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from sheetpipe.fetcher import fetch_sheet_data
from sheetpipe.loader import load_to_postgres
from sheetpipe.schema import infer_schema
from sheetpipe.validator import validate_rows
from sheetpipe.reporter import report_validation


@dataclass
class PipelineConfig:
    spreadsheet_id: str
    sheet_range: str
    pg_dsn: str
    table_name: str = ""
    drop_if_exists: bool = False
    drop_invalid: bool = True
    report_fmt: str = "text"
    credentials_file: str = "credentials.json"
    extra: dict[str, Any] = field(default_factory=dict)


def resolved_table_name(config: PipelineConfig) -> str:
    """Return the target table name, falling back to the sheet range slug."""
    if config.table_name:
        return config.table_name
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", config.sheet_range).strip("_").lower()
    return slug or "sheet_data"


def run_pipeline(config: PipelineConfig) -> dict[str, Any]:
    """Execute the full fetch → validate → load pipeline.

    Returns a summary dict with keys:
      - ``table``: destination table name
      - ``valid_rows``: number of rows loaded
      - ``invalid_rows``: number of rows dropped
      - ``columns``: inferred column count
    """
    headers, rows = fetch_sheet_data(
        config.spreadsheet_id,
        config.sheet_range,
        credentials_file=config.credentials_file,
    )

    validation = validate_rows(headers, rows, drop_invalid=config.drop_invalid)

    table = resolved_table_name(config)
    report_validation(validation, table_name=table, fmt=config.report_fmt)

    schema = infer_schema(headers, validation.valid_rows)

    rows_loaded = load_to_postgres(
        config.pg_dsn,
        table,
        headers,
        validation.valid_rows,
        schema,
        drop_if_exists=config.drop_if_exists,
    )

    return {
        "table": table,
        "valid_rows": rows_loaded,
        "invalid_rows": validation.error_count,
        "columns": len(headers),
    }
