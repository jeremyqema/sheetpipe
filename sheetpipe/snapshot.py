"""Snapshot module: capture and compare pipeline data snapshots for change detection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Snapshot:
    sheet_id: str
    tab_name: str
    row_count: int
    column_count: int
    checksum: str
    headers: List[str] = field(default_factory=list)


def _compute_checksum(headers: List[str], rows: List[List[str]]) -> str:
    """Return a SHA-256 hex digest of the serialised headers + rows."""
    payload = json.dumps({"headers": headers, "rows": rows}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_snapshot(sheet_id: str, tab_name: str, headers: List[str], rows: List[List[str]]) -> Snapshot:
    """Build a Snapshot from raw sheet data."""
    checksum = _compute_checksum(headers, rows)
    return Snapshot(
        sheet_id=sheet_id,
        tab_name=tab_name,
        row_count=len(rows),
        column_count=len(headers),
        checksum=checksum,
        headers=list(headers),
    )


def snapshots_differ(previous: Optional[Snapshot], current: Snapshot) -> bool:
    """Return True when the current snapshot differs from the previous one (or there is no previous)."""
    if previous is None:
        return True
    return previous.checksum != current.checksum


def snapshot_to_dict(snapshot: Snapshot) -> dict:
    """Serialise a Snapshot to a plain dict suitable for JSON storage."""
    return {
        "sheet_id": snapshot.sheet_id,
        "tab_name": snapshot.tab_name,
        "row_count": snapshot.row_count,
        "column_count": snapshot.column_count,
        "checksum": snapshot.checksum,
        "headers": snapshot.headers,
    }


def snapshot_from_dict(data: dict) -> Snapshot:
    """Deserialise a Snapshot from a plain dict."""
    return Snapshot(
        sheet_id=data["sheet_id"],
        tab_name=data["tab_name"],
        row_count=data["row_count"],
        column_count=data["column_count"],
        checksum=data["checksum"],
        headers=data.get("headers", []),
    )
