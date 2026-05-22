"""Join two datasets on a common key column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class JoinConfig:
    left_key: str
    right_key: str
    join_type: str = "inner"  # inner | left | right
    right_prefix: str = "right_"


@dataclass
class JoinResult:
    headers: List[str]
    rows: List[List[str]]
    unmatched_left: int = 0
    unmatched_right: int = 0
    warnings: List[str] = field(default_factory=list)


def _index_rows(
    headers: List[str], rows: List[List[str]], key: str
) -> Tuple[int, Dict[str, List[str]]]:
    if key not in headers:
        raise ValueError(f"Key column '{key}' not found in headers: {headers}")
    idx = headers.index(key)
    index: Dict[str, List[str]] = {}
    for row in rows:
        k = row[idx] if idx < len(row) else ""
        index.setdefault(k, row)
    return idx, index


def join_rows(
    left_headers: List[str],
    left_rows: List[List[str]],
    right_headers: List[str],
    right_rows: List[List[str]],
    config: JoinConfig,
) -> JoinResult:
    warnings: List[str] = []

    right_idx, right_index = _index_rows(right_headers, right_rows, config.right_key)

    right_extra = [
        h for i, h in enumerate(right_headers) if i != right_idx
    ]
    prefixed_right = [f"{config.right_prefix}{h}" for h in right_extra]
    merged_headers = left_headers + prefixed_right

    left_key_idx = left_headers.index(config.left_key) if config.left_key in left_headers else None
    if left_key_idx is None:
        raise ValueError(f"Key column '{config.left_key}' not found in left headers")

    empty_right = [""] * len(right_extra)
    matched_right_keys: set = set()
    result_rows: List[List[str]] = []
    unmatched_left = 0

    for row in left_rows:
        lk = row[left_key_idx] if left_key_idx < len(row) else ""
        if lk in right_index:
            matched_right_keys.add(lk)
            rrow = right_index[lk]
            rvals = [v for i, v in enumerate(rrow) if i != right_idx]
            result_rows.append(row + rvals)
        else:
            unmatched_left += 1
            if config.join_type == "left":
                result_rows.append(row + empty_right)
            elif config.join_type == "inner":
                pass

    unmatched_right = 0
    if config.join_type == "right":
        right_key_idx, _ = _index_rows(right_headers, right_rows, config.right_key)
        for rrow in right_rows:
            rk = rrow[right_key_idx] if right_key_idx < len(rrow) else ""
            if rk not in matched_right_keys:
                unmatched_right += 1
                empty_left = [""] * len(left_headers)
                rvals = [v for i, v in enumerate(rrow) if i != right_key_idx]
                result_rows.append(empty_left + rvals)

    if unmatched_left:
        warnings.append(f"{unmatched_left} left row(s) had no match in right dataset")

    return JoinResult(
        headers=merged_headers,
        rows=result_rows,
        unmatched_left=unmatched_left,
        unmatched_right=unmatched_right,
        warnings=warnings,
    )
