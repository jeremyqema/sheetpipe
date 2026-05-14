"""Simple file-based cache for sheet data to avoid redundant API calls."""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

DEFAULT_CACHE_DIR = ".sheetpipe_cache"
DEFAULT_TTL_SECONDS = 300  # 5 minutes


def _cache_key(spreadsheet_id: str, range_name: str) -> str:
    """Generate a stable filename key from spreadsheet ID and range."""
    raw = f"{spreadsheet_id}:{range_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_path(cache_dir: str, spreadsheet_id: str, range_name: str) -> str:
    key = _cache_key(spreadsheet_id, range_name)
    return os.path.join(cache_dir, f"{key}.json")


def read_cache(
    spreadsheet_id: str,
    range_name: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> Optional[list]:
    """Return cached rows if present and not expired, else None."""
    path = _cache_path(cache_dir, spreadsheet_id, range_name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    cached_at = datetime.fromisoformat(payload["cached_at"])
    if datetime.utcnow() - cached_at > timedelta(seconds=ttl_seconds):
        os.remove(path)
        return None
    return payload["rows"]


def write_cache(
    spreadsheet_id: str,
    range_name: str,
    rows: list,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> None:
    """Persist rows to the cache directory."""
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(cache_dir, spreadsheet_id, range_name)
    payload = {
        "cached_at": datetime.utcnow().isoformat(),
        "spreadsheet_id": spreadsheet_id,
        "range": range_name,
        "rows": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def invalidate_cache(
    spreadsheet_id: str,
    range_name: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> bool:
    """Remove a specific cache entry. Returns True if a file was deleted."""
    path = _cache_path(cache_dir, spreadsheet_id, range_name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
