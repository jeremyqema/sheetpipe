"""Row-level data transformation utilities for sheetpipe."""

from typing import Any, Optional


def coerce_value(value: str, pg_type: str) -> Optional[Any]:
    """Coerce a raw string cell value to a Python type matching the inferred PG type."""
    if value is None or value.strip() == "":
        return None

    v = value.strip()

    if pg_type == "INTEGER":
        try:
            return int(v.replace(",", ""))
        except ValueError:
            return None

    if pg_type == "NUMERIC":
        try:
            return float(v.replace(",", ""))
        except ValueError:
            return None

    if pg_type == "BOOLEAN":
        if v.lower() in ("true", "yes", "1"):
            return True
        if v.lower() in ("false", "no", "0"):
            return False
        return None

    # TEXT — return as-is
    return v


def transform_row(
    row: list[str],
    headers: list[str],
    schema: dict[str, str],
) -> dict[str, Optional[Any]]:
    """Transform a raw row list into a typed dict keyed by sanitized header names.

    Args:
        row: Raw cell values aligned with *headers*.
        headers: Column names (already sanitized identifiers).
        schema: Mapping of header name -> PostgreSQL type string.

    Returns:
        Dict of {column: coerced_value}.
    """
    result: dict[str, Optional[Any]] = {}
    for i, header in enumerate(headers):
        raw = row[i] if i < len(row) else ""
        pg_type = schema.get(header, "TEXT")
        result[header] = coerce_value(raw, pg_type)
    return result


def transform_rows(
    rows: list[list[str]],
    headers: list[str],
    schema: dict[str, str],
) -> list[dict[str, Optional[Any]]]:
    """Apply :func:`transform_row` to every row."""
    return [transform_row(row, headers, schema) for row in rows]
