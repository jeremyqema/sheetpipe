"""Load FilterConfig definitions from a dict/JSON structure."""
from __future__ import annotations

from typing import Any, Dict, List

from sheetpipe.filter import FilterConfig

VALID_OPERATORS = {"eq", "neq", "gt", "lt", "gte", "lte", "contains", "startswith"}


class FilterConfigError(ValueError):
    """Raised when a filter definition is invalid."""


def _parse_one(raw: Dict[str, Any], index: int) -> FilterConfig:
    """Parse a single filter definition dict."""
    if "column" not in raw:
        raise FilterConfigError(f"Filter #{index}: missing required key 'column'")
    if "operator" not in raw:
        raise FilterConfigError(f"Filter #{index}: missing required key 'operator'")
    if "value" not in raw:
        raise FilterConfigError(f"Filter #{index}: missing required key 'value'")

    operator = raw["operator"]
    if operator not in VALID_OPERATORS:
        raise FilterConfigError(
            f"Filter #{index}: unknown operator '{operator}'. "
            f"Valid operators: {sorted(VALID_OPERATORS)}"
        )

    return FilterConfig(
        column=str(raw["column"]),
        operator=operator,
        value=raw["value"],
        case_sensitive=bool(raw.get("case_sensitive", True)),
    )


def load_filter_configs(raw_filters: List[Dict[str, Any]]) -> List[FilterConfig]:
    """Parse a list of raw filter dicts into FilterConfig objects.

    Args:
        raw_filters: list of dicts, each with keys: column, operator, value,
                     and optionally case_sensitive.

    Returns:
        List of validated FilterConfig instances.

    Raises:
        FilterConfigError: if any filter definition is malformed.
    """
    if not isinstance(raw_filters, list):
        raise FilterConfigError("filters must be a list")
    return [_parse_one(item, i) for i, item in enumerate(raw_filters)]
