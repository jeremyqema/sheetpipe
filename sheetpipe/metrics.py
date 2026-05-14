"""Lightweight in-process metrics collection for pipeline runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PipelineMetrics:
    """Holds counters and timing information for a single pipeline run."""

    rows_fetched: int = 0
    rows_valid: int = 0
    rows_invalid: int = 0
    rows_inserted: int = 0
    validation_errors: int = 0
    retries: int = 0
    duration_seconds: float = 0.0
    extra: Dict[str, object] = field(default_factory=dict)

    # Internal wall-clock start time (not serialised).
    _start: Optional[float] = field(default=None, repr=False, compare=False)

    def start_timer(self) -> None:
        """Record the start time."""
        self._start = time.monotonic()

    def stop_timer(self) -> None:
        """Compute elapsed duration from the recorded start time."""
        if self._start is not None:
            self.duration_seconds = time.monotonic() - self._start
            self._start = None

    def to_dict(self) -> dict:
        """Return a plain dict representation suitable for logging or JSON."""
        return {
            "rows_fetched": self.rows_fetched,
            "rows_valid": self.rows_valid,
            "rows_invalid": self.rows_invalid,
            "rows_inserted": self.rows_inserted,
            "validation_errors": self.validation_errors,
            "retries": self.retries,
            "duration_seconds": round(self.duration_seconds, 4),
            **self.extra,
        }


def merge_metrics(base: PipelineMetrics, other: PipelineMetrics) -> PipelineMetrics:
    """Return a new PipelineMetrics that sums numeric fields from *base* and *other*."""
    merged_extra = {**base.extra, **other.extra}
    return PipelineMetrics(
        rows_fetched=base.rows_fetched + other.rows_fetched,
        rows_valid=base.rows_valid + other.rows_valid,
        rows_invalid=base.rows_invalid + other.rows_invalid,
        rows_inserted=base.rows_inserted + other.rows_inserted,
        validation_errors=base.validation_errors + other.validation_errors,
        retries=base.retries + other.retries,
        duration_seconds=base.duration_seconds + other.duration_seconds,
        extra=merged_extra,
    )
