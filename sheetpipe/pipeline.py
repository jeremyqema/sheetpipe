"""High-level pipeline: fetch a Google Sheet and sync it to PostgreSQL."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sheetpipe.fetcher import fetch_sheet_data
from sheetpipe.loader import load_to_postgres

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for a single sheet-to-table sync."""

    spreadsheet_id: str
    sheet_name: str
    pg_dsn: str
    table_name: str | None = None  # defaults to sheet_name
    credentials_path: str | None = None
    drop_if_exists: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def resolved_table_name(self) -> str:
        return self.table_name or self.sheet_name


def run_pipeline(config: PipelineConfig) -> int:
    """Execute a full fetch-and-load pipeline for one sheet.

    Returns:
        Number of rows synced.
    """
    logger.info(
        "Fetching sheet '%s' from spreadsheet '%s'",
        config.sheet_name,
        config.spreadsheet_id,
    )
    headers, rows = fetch_sheet_data(
        spreadsheet_id=config.spreadsheet_id,
        sheet_name=config.sheet_name,
        credentials_path=config.credentials_path,
    )

    if not headers:
        logger.warning("Sheet '%s' appears to be empty — skipping.", config.sheet_name)
        return 0

    logger.info(
        "Loaded %d rows with %d columns; syncing to table '%s'",
        len(rows),
        len(headers),
        config.resolved_table_name,
    )
    count = load_to_postgres(
        dsn=config.pg_dsn,
        table_name=config.resolved_table_name,
        headers=headers,
        rows=rows,
        drop_if_exists=config.drop_if_exists,
    )
    logger.info("Synced %d rows to '%s'.", count, config.resolved_table_name)
    return count
