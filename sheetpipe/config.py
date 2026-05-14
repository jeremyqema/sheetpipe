"""Configuration loading from environment variables and .env files."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvConfig:
    """Settings resolved from environment variables."""

    spreadsheet_id: str
    sheet_range: str
    dsn: str
    table_name: Optional[str] = None
    drop_if_exists: bool = False
    drop_invalid_rows: bool = True
    report_format: str = "text"
    credentials_path: Optional[str] = None


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_env_config() -> EnvConfig:
    """Load pipeline configuration from environment variables.

    Required variables:
        SHEETPIPE_SPREADSHEET_ID
        SHEETPIPE_SHEET_RANGE
        SHEETPIPE_DSN

    Optional variables:
        SHEETPIPE_TABLE_NAME
        SHEETPIPE_DROP_IF_EXISTS  (default: false)
        SHEETPIPE_DROP_INVALID_ROWS  (default: true)
        SHEETPIPE_REPORT_FORMAT  (default: text)
        GOOGLE_APPLICATION_CREDENTIALS
    """
    missing = []
    for key in ("SHEETPIPE_SPREADSHEET_ID", "SHEETPIPE_SHEET_RANGE", "SHEETPIPE_DSN"):
        if not os.environ.get(key):
            missing.append(key)
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return EnvConfig(
        spreadsheet_id=os.environ["SHEETPIPE_SPREADSHEET_ID"],
        sheet_range=os.environ["SHEETPIPE_SHEET_RANGE"],
        dsn=os.environ["SHEETPIPE_DSN"],
        table_name=os.environ.get("SHEETPIPE_TABLE_NAME") or None,
        drop_if_exists=_parse_bool(os.environ.get("SHEETPIPE_DROP_IF_EXISTS", "false")),
        drop_invalid_rows=_parse_bool(
            os.environ.get("SHEETPIPE_DROP_INVALID_ROWS", "true")
        ),
        report_format=os.environ.get("SHEETPIPE_REPORT_FORMAT", "text"),
        credentials_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or None,
    )
