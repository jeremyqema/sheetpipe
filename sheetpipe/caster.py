"""Column-level type casting: apply explicit pg-type casts to row data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CastConfig:
    """Maps column names to desired PostgreSQL types for explicit casting."""
    column_types: Dict[str, str] = field(default_factory=dict)  # col -> pg type
    strict: bool = False  # if True, raise on cast failure; else use None


@dataclass
class CastResult:
    rows: List[List[Any]]
    warnings: List[str] = field(default_factory=list)
    cast_count: int = 0


_BOOL_TRUE = {"true", "yes", "1", "t", "y"}
_BOOL_FALSE = {"false", "no", "0", "f", "n"}


def _cast_value(value: Any, pg_type: str, strict: bool) -> Tuple[Any, Optional[str]]:
    """Attempt to cast *value* to *pg_type*. Returns (cast_value, warning_or_None)."""
    raw = str(value).strip() if value is not None else ""
    t = pg_type.lower().split("(")[0].strip()

    try:
        if t in ("integer", "bigint", "smallint", "int"):
            return int(raw.replace(",", "")), None
        if t in ("numeric", "float", "double precision", "real", "decimal"):
            return float(raw.replace(",", "")), None
        if t == "boolean":
            if raw.lower() in _BOOL_TRUE:
                return True, None
            if raw.lower() in _BOOL_FALSE:
                return False, None
            raise ValueError(f"Cannot cast {raw!r} to boolean")
        if t in ("text", "varchar", "character varying", "char"):
            return raw, None
        # Unknown type: pass through
        return value, None
    except (ValueError, TypeError) as exc:
        msg = f"Cast failed for value {value!r} -> {pg_type}: {exc}"
        if strict:
            raise ValueError(msg) from exc
        return None, msg


def cast_rows(
    headers: List[str],
    rows: List[List[Any]],
    config: CastConfig,
) -> CastResult:
    """Apply explicit type casts defined in *config* to every row."""
    if not config.column_types:
        return CastResult(rows=rows)

    col_index: Dict[str, int] = {h: i for i, h in enumerate(headers)}
    unknown = set(config.column_types) - set(col_index)
    warnings: List[str] = [
        f"Cast config references unknown column: {c!r}" for c in sorted(unknown)
    ]

    cast_count = 0
    result_rows: List[List[Any]] = []

    for row in rows:
        new_row = list(row)
        for col, pg_type in config.column_types.items():
            idx = col_index.get(col)
            if idx is None or idx >= len(new_row):
                continue
            casted, warn = _cast_value(new_row[idx], pg_type, config.strict)
            if warn:
                warnings.append(warn)
            else:
                cast_count += 1
            new_row[idx] = casted
        result_rows.append(new_row)

    return CastResult(rows=result_rows, warnings=warnings, cast_count=cast_count)
