from __future__ import annotations

from typing import Any, Dict

from sheetpipe.flattener import FlattenConfig


class FlattenConfigError(ValueError):
    """Raised when a flatten configuration dict is invalid."""


def load_flatten_config(raw: Dict[str, Any]) -> FlattenConfig:
    """Parse a flatten configuration from a plain dict (e.g. loaded from YAML/JSON).

    Expected keys:
        column (str, required)  — name of the column to flatten
        delimiter (str)         — segment separator, default ','
        strip_whitespace (bool) — trim segments, default True
        skip_empty (bool)       — drop empty segments, default True
    """
    if "column" not in raw or not raw["column"]:
        raise FlattenConfigError("flatten config requires a non-empty 'column' field")

    column: str = str(raw["column"])
    delimiter: str = str(raw.get("delimiter", ","))
    if not delimiter:
        raise FlattenConfigError("flatten config 'delimiter' must not be empty")

    strip_whitespace: bool = bool(raw.get("strip_whitespace", True))
    skip_empty: bool = bool(raw.get("skip_empty", True))

    return FlattenConfig(
        column=column,
        delimiter=delimiter,
        strip_whitespace=strip_whitespace,
        skip_empty_segments=skip_empty,
    )
