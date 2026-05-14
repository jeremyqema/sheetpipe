"""Google Sheets data fetcher using the Sheets API v4."""

from __future__ import annotations

import os
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _build_service(credentials_path: str | None = None):
    """Build and return an authenticated Google Sheets service client."""
    creds_file = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_file:
        raise ValueError(
            "Credentials path must be provided or set via "
            "GOOGLE_APPLICATION_CREDENTIALS environment variable."
        )
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def fetch_sheet_data(
    spreadsheet_id: str,
    sheet_name: str,
    credentials_path: str | None = None,
) -> tuple[list[str], list[list[Any]]]:
    """Fetch header row and data rows from a Google Sheet.

    Returns:
        A tuple of (headers, rows) where headers is a list of column names
        and rows is a list of value lists.
    """
    service = _build_service(credentials_path)
    range_name = f"{sheet_name}"
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
    except HttpError as exc:
        raise RuntimeError(
            f"Failed to fetch sheet '{sheet_name}' from spreadsheet '{spreadsheet_id}': {exc}"
        ) from exc

    values: list[list[Any]] = result.get("values", [])
    if not values:
        return [], []

    headers: list[str] = [str(h) for h in values[0]]
    rows = values[1:]

    # Pad rows that are shorter than the header row
    padded_rows = [
        row + [""] * (len(headers) - len(row)) if len(row) < len(headers) else row
        for row in rows
    ]
    return headers, padded_rows
