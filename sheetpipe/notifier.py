"""Pipeline run notification support (stdout, webhook)."""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Optional

from sheetpipe.audit import AuditEntry


@dataclass
class NotifierConfig:
    webhook_url: Optional[str] = None
    silent: bool = False


def _format_message(entry: AuditEntry) -> str:
    status = "✅" if entry.error is None else "❌"
    parts = [
        f"{status} sheetpipe | table={entry.table_name}",
        f"rows_fetched={entry.rows_fetched}",
        f"rows_inserted={entry.rows_inserted}",
        f"duration={entry.duration_seconds:.2f}s",
    ]
    if entry.error:
        parts.append(f"error={entry.error}")
    return "  ".join(parts)


def notify_stdout(entry: AuditEntry, config: NotifierConfig) -> None:
    """Print a one-line summary to stdout unless silent."""
    if config.silent:
        return
    print(_format_message(entry))


def notify_webhook(entry: AuditEntry, config: NotifierConfig) -> bool:
    """POST audit entry as JSON to the configured webhook URL.

    Returns True on success, False on any network/HTTP error.
    """
    if not config.webhook_url:
        return False
    payload = json.dumps(
        {
            "table": entry.table_name,
            "rows_fetched": entry.rows_fetched,
            "rows_inserted": entry.rows_inserted,
            "duration_seconds": entry.duration_seconds,
            "error": entry.error,
            "timestamp": entry.timestamp,
        }
    ).encode()
    req = urllib.request.Request(
        config.webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False


def notify(entry: AuditEntry, config: NotifierConfig) -> None:
    """Run all configured notification channels."""
    notify_stdout(entry, config)
    notify_webhook(entry, config)
