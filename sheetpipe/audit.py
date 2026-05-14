"""Audit log module for sheetpipe pipeline runs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class AuditEntry:
    timestamp: str
    sheet_id: str
    table_name: str
    rows_fetched: int
    rows_inserted: int
    rows_invalid: int
    status: str  # "success" | "failure"
    error: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "sheet_id": self.sheet_id,
            "table_name": self.table_name,
            "rows_fetched": self.rows_fetched,
            "rows_inserted": self.rows_inserted,
            "rows_invalid": self.rows_invalid,
            "status": self.status,
            "error": self.error,
            **self.extra,
        }


def make_entry(
    sheet_id: str,
    table_name: str,
    rows_fetched: int,
    rows_inserted: int,
    rows_invalid: int,
    status: str,
    error: Optional[str] = None,
    **extra: Any,
) -> AuditEntry:
    """Create an AuditEntry with a UTC ISO-8601 timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return AuditEntry(
        timestamp=ts,
        sheet_id=sheet_id,
        table_name=table_name,
        rows_fetched=rows_fetched,
        rows_inserted=rows_inserted,
        rows_invalid=rows_invalid,
        status=status,
        error=error,
        extra=extra,
    )


def append_audit_log(entry: AuditEntry, log_path: str) -> None:
    """Append a JSON-lines record to *log_path*."""
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.to_dict()) + "\n")


def read_audit_log(log_path: str) -> List[Dict[str, Any]]:
    """Return all entries from a JSON-lines audit log file."""
    if not os.path.exists(log_path):
        return []
    entries: List[Dict[str, Any]] = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
