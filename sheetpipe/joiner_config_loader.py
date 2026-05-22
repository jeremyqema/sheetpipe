"""Load JoinConfig from a plain dict (e.g. parsed from JSON/YAML CLI arg)."""
from __future__ import annotations

from typing import Any, Dict

from sheetpipe.joiner import JoinConfig

VALID_JOIN_TYPES = {"inner", "left", "right"}


class JoinConfigError(ValueError):
    """Raised when join configuration is invalid."""


def load_join_config(data: Dict[str, Any]) -> JoinConfig:
    """Parse and validate a join configuration dictionary.

    Expected keys:
        left_key  (str, required)
        right_key (str, required)
        join_type (str, optional, default 'inner')
        right_prefix (str, optional, default 'right_')
    """
    if not isinstance(data, dict):
        raise JoinConfigError("Join config must be a mapping")

    left_key = data.get("left_key")
    if not left_key or not isinstance(left_key, str):
        raise JoinConfigError("'left_key' is required and must be a non-empty string")

    right_key = data.get("right_key")
    if not right_key or not isinstance(right_key, str):
        raise JoinConfigError("'right_key' is required and must be a non-empty string")

    join_type = data.get("join_type", "inner")
    if join_type not in VALID_JOIN_TYPES:
        raise JoinConfigError(
            f"'join_type' must be one of {sorted(VALID_JOIN_TYPES)}, got '{join_type}'"
        )

    right_prefix = data.get("right_prefix", "right_")
    if not isinstance(right_prefix, str):
        raise JoinConfigError("'right_prefix' must be a string")

    return JoinConfig(
        left_key=left_key,
        right_key=right_key,
        join_type=join_type,
        right_prefix=right_prefix,
    )
