"""Fetch data from Google Sheets, with optional local caching."""

from __future__ import annotations

from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

from sheetpipe.cache import read_cache, write_cache

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _build_service(credentials_path: str):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def fetch_sheet_data(
    spreadsheet_id: str,
    range_name: str,
    credentials_path: str,
    use_cache: bool = False,
    cache_ttl: int = 300,
    cache_dir: str = ".sheetpipe_cache",
) -> tuple[list[str], list[list[str]]]:
    """Return (headers, rows) from a Google Sheet range.

    When *use_cache* is True the result is read from / written to a local
    JSON cache so repeated runs avoid unnecessary API calls.
    """
    if use_cache:
        cached = read_cache(
            spreadsheet_id, range_name, ttl_seconds=cache_ttl, cache_dir=cache_dir
        )
        if cached is not None:
            if not cached:
                return [], []
            headers = cached[0]
            rows = cached[1:]
            return headers, rows

    service = _build_service(credentials_path)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    all_rows: list[list[str]] = result.get("values", [])

    if not all_rows:
        if use_cache:
            write_cache(spreadsheet_id, range_name, [], cache_dir=cache_dir)
        return [], []

    headers = [str(h) for h in all_rows[0]]
    num_cols = len(headers)
    rows: list[list[str]] = []
    for raw in all_rows[1:]:
        padded = [str(v) for v in raw] + [""] * (num_cols - len(raw))
        rows.append(padded[:num_cols])

    if use_cache:
        write_cache(spreadsheet_id, range_name, [headers] + rows, cache_dir=cache_dir)

    return headers, rows
