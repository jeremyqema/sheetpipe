"""Load deduplication configuration from a plain dict (e.g. parsed from JSON/YAML)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class DedupConfigError(ValueError):
    """Raised when a dedup configuration dict is invalid."""


def load_dedup_config(
    raw: Dict[str, Any],
) -> tuple[Optional[List[str]], str]:
    """Parse and validate a dedup configuration dictionary.

    Expected shape::

        {
            "key_columns": ["id", "date"],   # optional
            "keep": "first"                   # optional, default 'first'
        }

    Returns:
        A tuple of (key_columns, keep) ready to pass to deduplicate_rows.

    Raises:
        DedupConfigError: if the config is structurally invalid.
    """
    if not isinstance(raw, dict):
        raise DedupConfigError(f"Dedup config must be a dict, got {type(raw).__name__}")

    key_columns: Optional[List[str]] = raw.get("key_columns")
    if key_columns is not None:
        if not isinstance(key_columns, list) or not all(
            isinstance(c, str) for c in key_columns
        ):
            raise DedupConfigError("'key_columns' must be a list of strings")
        if len(key_columns) == 0:
            raise DedupConfigError("'key_columns' must not be empty when provided")

    keep: str = raw.get("keep", "first")
    if keep not in ("first", "last"):
        raise DedupConfigError(f"'keep' must be 'first' or 'last', got {keep!r}")

    return key_columns, keep
