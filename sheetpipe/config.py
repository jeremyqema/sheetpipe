"""Environment-based configuration loader for sheetpipe."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvConfig:
    spreadsheet_id: str
    pg_dsn: str
    google_credentials_file: str
    table_prefix: str = ""
    drop_if_exists: bool = False
    cache_ttl_seconds: int = 300
    webhook_url: Optional[str] = None
    silent_notifications: bool = False


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_env_config(env: Optional[dict[str, str]] = None) -> EnvConfig:
    """Load configuration from environment variables.

    Args:
        env: Optional mapping to use instead of ``os.environ`` (useful in tests).

    Raises:
        KeyError: if a required variable is absent.
    """
    src = env if env is not None else os.environ

    missing = [
        k
        for k in ("SHEETPIPE_SPREADSHEET_ID", "SHEETPIPE_PG_DSN", "GOOGLE_CREDENTIALS_FILE")
        if k not in src
    ]
    if missing:
        raise KeyError(f"Missing required environment variables: {', '.join(missing)}")

    return EnvConfig(
        spreadsheet_id=src["SHEETPIPE_SPREADSHEET_ID"],
        pg_dsn=src["SHEETPIPE_PG_DSN"],
        google_credentials_file=src["GOOGLE_CREDENTIALS_FILE"],
        table_prefix=src.get("SHEETPIPE_TABLE_PREFIX", ""),
        drop_if_exists=_parse_bool(src.get("SHEETPIPE_DROP_IF_EXISTS", "false")),
        cache_ttl_seconds=int(src.get("SHEETPIPE_CACHE_TTL", "300")),
        webhook_url=src.get("SHEETPIPE_WEBHOOK_URL"),
        silent_notifications=_parse_bool(src.get("SHEETPIPE_SILENT", "false")),
    )
