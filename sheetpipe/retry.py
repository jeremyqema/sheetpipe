"""Retry utility with exponential backoff for transient failures."""

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Callable, Iterable, Type, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)

_DEFAULT_RETRYABLE: tuple[Type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def retry(
    *,
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: Iterable[Type[Exception]] = _DEFAULT_RETRYABLE,
) -> Callable[[F], F]:
    """Decorator that retries a function on retryable exceptions.

    Args:
        max_attempts: Total number of attempts (including the first call).
        backoff_base: Initial sleep duration in seconds before the first retry.
        backoff_multiplier: Factor by which the sleep duration grows each retry.
        retryable_exceptions: Exception types that should trigger a retry.

    Returns:
        Decorated function that will be retried on failure.
    """
    exc_tuple = tuple(retryable_exceptions)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = backoff_base
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exc_tuple as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.error(
                            "[retry] %s failed after %d attempts: %s",
                            func.__qualname__,
                            max_attempts,
                            exc,
                        )
                        raise
                    logger.warning(
                        "[retry] %s attempt %d/%d failed (%s). Retrying in %.1fs.",
                        func.__qualname__,
                        attempt,
                        max_attempts,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= backoff_multiplier
            raise RuntimeError("Unreachable")  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator


def with_retry(
    func: Callable,
    *args,
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: Iterable[Type[Exception]] = _DEFAULT_RETRYABLE,
    **kwargs,
):
    """Functional interface to retry a callable without using the decorator."""
    decorated = retry(
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        backoff_multiplier=backoff_multiplier,
        retryable_exceptions=retryable_exceptions,
    )(func)
    return decorated(*args, **kwargs)
