"""Load EnrichmentConfig objects from a list of plain dicts (e.g. parsed from JSON/YAML)."""
from __future__ import annotations

from typing import Any, Dict, List

from sheetpipe.enricher import EnrichmentConfig

_BUILTINS: Dict[str, Any] = {"__builtins__": {}}


class EnricherConfigError(ValueError):
    """Raised when an enrichment config entry is invalid."""


def _parse_one(raw: dict) -> EnrichmentConfig:
    """Parse a single enrichment spec dict into an EnrichmentConfig.

    Expected keys:
      - column_name (str, required)
      - expression  (str, required) — a Python lambda body, e.g. "row['a'] + row['b']"
      - default     (str, optional)
    """
    if "column_name" not in raw:
        raise EnricherConfigError("Enrichment entry missing 'column_name'")
    if "expression" not in raw:
        raise EnricherConfigError(
            f"Enrichment entry '{raw['column_name']}' missing 'expression'"
        )

    column_name: str = str(raw["column_name"]).strip()
    expr_src: str = raw["expression"]
    default: str | None = raw.get("default", None)

    try:
        fn = eval(f"lambda row: {expr_src}", _BUILTINS)  # noqa: S307
    except SyntaxError as exc:
        raise EnricherConfigError(
            f"Invalid expression for '{column_name}': {exc}"
        ) from exc

    return EnrichmentConfig(column_name=column_name, expression=fn, default=default)


def load_enricher_configs(raw_list: List[dict]) -> List[EnrichmentConfig]:
    """Parse a list of enrichment spec dicts."""
    if not raw_list:
        return []
    return [_parse_one(entry) for entry in raw_list]
