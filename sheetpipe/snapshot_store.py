"""Persistent storage for Snapshot objects, backed by a JSON file on disk."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from sheetpipe.snapshot import Snapshot, snapshot_from_dict, snapshot_to_dict

_DEFAULT_STORE_PATH = Path(os.environ.get("SHEETPIPE_SNAPSHOT_DIR", ".sheetpipe")) / "snapshots.json"


def _load_store(store_path: Path) -> dict:
    if not store_path.exists():
        return {}
    try:
        with store_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: dict, store_path: Path) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)


def _store_key(sheet_id: str, tab_name: str) -> str:
    return f"{sheet_id}::{tab_name}"


def load_snapshot(
    sheet_id: str,
    tab_name: str,
    store_path: Path = _DEFAULT_STORE_PATH,
) -> Optional[Snapshot]:
    """Return the persisted Snapshot for the given sheet/tab, or None if absent."""
    store = _load_store(store_path)
    key = _store_key(sheet_id, tab_name)
    entry = store.get(key)
    if entry is None:
        return None
    return snapshot_from_dict(entry)


def save_snapshot(
    snapshot: Snapshot,
    store_path: Path = _DEFAULT_STORE_PATH,
) -> None:
    """Persist a Snapshot, overwriting any previous entry for the same sheet/tab."""
    store = _load_store(store_path)
    key = _store_key(snapshot.sheet_id, snapshot.tab_name)
    store[key] = snapshot_to_dict(snapshot)
    _save_store(store, store_path)


def delete_snapshot(
    sheet_id: str,
    tab_name: str,
    store_path: Path = _DEFAULT_STORE_PATH,
) -> bool:
    """Remove a stored snapshot. Returns True if an entry was removed."""
    store = _load_store(store_path)
    key = _store_key(sheet_id, tab_name)
    if key not in store:
        return False
    del store[key]
    _save_store(store, store_path)
    return True
