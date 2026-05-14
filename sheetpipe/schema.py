"""Schema inference module for deriving PostgreSQL column types from Google Sheets data."""

from typing import Any


PG_TYPE_MAP = {
    "integer": "INTEGER",
    "float": "DOUBLE PRECISION",
    "boolean": "BOOLEAN",
    "date": "DATE",
    "timestamp": "TIMESTAMP",
    "text": "TEXT",
}


def infer_pg_type(values: list[Any]) -> str:
    """Infer the most appropriate PostgreSQL type from a list of sample values."""
    non_null = [v for v in values if v is not None and v != ""]
    if not non_null:
        return "TEXT"

    if all(_is_boolean(v) for v in non_null):
        return PG_TYPE_MAP["boolean"]
    if all(_is_integer(v) for v in non_null):
        return PG_TYPE_MAP["integer"]
    if all(_is_float(v) for v in non_null):
        return PG_TYPE_MAP["float"]
    return PG_TYPE_MAP["text"]


def infer_schema(headers: list[str], rows: list[list[Any]]) -> dict[str, str]:
    """Return a mapping of column name -> PostgreSQL type for the given sheet data."""
    schema: dict[str, str] = {}
    for idx, header in enumerate(headers):
        column_values = [row[idx] if idx < len(row) else None for row in rows]
        schema[header] = infer_pg_type(column_values)
    return schema


def _is_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    return str(value).strip().lower() in {"true", "false", "yes", "no", "1", "0"}


def _is_integer(value: Any) -> bool:
    try:
        int(str(value).strip())
        return True
    except ValueError:
        return False


def _is_float(value: Any) -> bool:
    try:
        float(str(value).strip())
        return True
    except ValueError:
        return False
