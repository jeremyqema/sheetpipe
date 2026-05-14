"""Row-level validation utilities for sheetpipe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    valid_rows: list[list[Any]] = field(default_factory=list)
    invalid_rows: list[tuple[int, list[Any], str]] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.invalid_rows) > 0

    @property
    def error_count(self) -> int:
        return len(self.invalid_rows)


def validate_rows(
    headers: list[str],
    rows: list[list[Any]],
    *,
    drop_invalid: bool = True,
) -> ValidationResult:
    """Validate rows against headers.

    Checks performed:
    - Row length matches header length (padded or truncated rows are flagged).
    - Completely empty rows are dropped with a warning.

    Args:
        headers: Column names inferred from the sheet.
        rows: Data rows to validate.
        drop_invalid: When True, invalid rows are excluded from valid_rows.

    Returns:
        ValidationResult with separated valid / invalid rows.
    """
    result = ValidationResult()
    expected = len(headers)

    for idx, row in enumerate(rows):
        if all(cell == "" or cell is None for cell in row):
            result.invalid_rows.append((idx, row, "empty row"))
            continue

        if len(row) != expected:
            reason = (
                f"column count mismatch: expected {expected}, got {len(row)}"
            )
            result.invalid_rows.append((idx, row, reason))
            if not drop_invalid:
                result.valid_rows.append(row)
            continue

        result.valid_rows.append(row)

    return result
