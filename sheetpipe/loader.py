"""PostgreSQL loader: create tables and insert rows from sheet data."""

from __future__ import annotations

from typing import Any

import psycopg2
import psycopg2.extras

from sheetpipe.ddl import build_create_table, build_insert, sanitize_identifier
from sheetpipe.schema import infer_schema


def load_to_postgres(
    dsn: str,
    table_name: str,
    headers: list[str],
    rows: list[list[Any]],
    drop_if_exists: bool = False,
) -> int:
    """Create (or replace) a table and bulk-insert sheet rows.

    Args:
        dsn: libpq connection string.
        table_name: Target PostgreSQL table name (will be sanitized).
        headers: Column names from the sheet header row.
        rows: Data rows, each a list aligned with *headers*.
        drop_if_exists: When True, DROP TABLE before creating.

    Returns:
        Number of rows inserted.
    """
    if not headers:
        return 0

    schema = infer_schema(headers, rows)
    safe_table = sanitize_identifier(table_name)
    create_sql = build_create_table(safe_table, schema)
    insert_sql = build_insert(safe_table, headers)

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            if drop_if_exists:
                cur.execute(f'DROP TABLE IF EXISTS "{safe_table}" CASCADE;')
            cur.execute(create_sql)

            if rows:
                # Convert rows (lists) to dicts keyed by sanitized column name
                col_names = [sanitize_identifier(h) for h in headers]
                records = [
                    dict(zip(col_names, row))
                    for row in rows
                ]
                psycopg2.extras.execute_batch(cur, insert_sql, records)

        conn.commit()

    return len(rows)
