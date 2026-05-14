"""DDL generation utilities — build CREATE TABLE statements from inferred schemas."""

import re


def sanitize_identifier(name: str) -> str:
    """Convert a raw header string into a safe PostgreSQL identifier."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name)
    name = name.strip("_")
    if not name or name[0].isdigit():
        name = "col_" + name
    return name


def build_create_table(
    table_name: str,
    schema: dict[str, str],
    if_not_exists: bool = True,
) -> str:
    """Generate a CREATE TABLE DDL statement from a schema mapping."""
    safe_table = sanitize_identifier(table_name)
    columns = []
    for raw_col, pg_type in schema.items():
        safe_col = sanitize_identifier(raw_col)
        columns.append(f"    {safe_col} {pg_type}")

    exists_clause = "IF NOT EXISTS " if if_not_exists else ""
    col_block = ",\n".join(columns)
    return f"CREATE TABLE {exists_clause}{safe_table} (\n{col_block}\n);"


def build_insert(
    table_name: str,
    headers: list[str],
) -> str:
    """Generate a parameterised INSERT statement for the given table and headers."""
    safe_table = sanitize_identifier(table_name)
    safe_cols = [sanitize_identifier(h) for h in headers]
    col_list = ", ".join(safe_cols)
    placeholders = ", ".join(f"%({h})s" for h in safe_cols)
    return f"INSERT INTO {safe_table} ({col_list}) VALUES ({placeholders});"
