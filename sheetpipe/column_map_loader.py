"""Load ColumnMapConfig from a plain dict (e.g. parsed from JSON/YAML)."""
from __future__ import annotations

from typing import Any, Dict

from sheetpipe.column_map import ColumnMapConfig


class ColumnMapConfigError(ValueError):
    """Raised when the column map configuration is malformed."""


def load_column_map_config(raw: Dict[str, Any]) -> ColumnMapConfig:
    """Parse a raw dictionary into a :class:`ColumnMapConfig`.

    Expected shape (all keys optional)::

        {
          "rename": {"Old Name": "new_name"},
          "order":  ["col_a", "col_b"],
          "drop":   ["unwanted_col"]
        }
    """
    rename = raw.get("rename", {})
    order = raw.get("order", [])
    drop = raw.get("drop", [])

    if not isinstance(rename, dict):
        raise ColumnMapConfigError("'rename' must be a dict mapping original names to new names")
    if not isinstance(order, list):
        raise ColumnMapConfigError("'order' must be a list of column names")
    if not isinstance(drop, list):
        raise ColumnMapConfigError("'drop' must be a list of column names")

    for k, v in rename.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ColumnMapConfigError(
                f"'rename' keys and values must be strings, got {k!r}: {v!r}"
            )

    for item in order:
        if not isinstance(item, str):
            raise ColumnMapConfigError(f"'order' entries must be strings, got {item!r}")

    for item in drop:
        if not isinstance(item, str):
            raise ColumnMapConfigError(f"'drop' entries must be strings, got {item!r}")

    return ColumnMapConfig(rename=rename, order=order, drop=drop)
