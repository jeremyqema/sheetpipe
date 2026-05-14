"""Tests for sheetpipe.retry module."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from sheetpipe.retry import retry, with_retry


# ---------------------------------------------------------------------------
# @retry decorator
# ---------------------------------------------------------------------------

def test_retry_succeeds_on_first_attempt():
    call_count = 0

    @retry(max_attempts=3, backoff_base=0)
    def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = succeed()
    assert result == "ok"
    assert call_count == 1


def test_retry_retries_on_retryable_exception():
    call_count = 0

    @retry(max_attempts=3, backoff_base=0, retryable_exceptions=(ConnectionError,))
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("transient")
        return "recovered"

    with patch("sheetpipe.retry.time.sleep"):
        result = flaky()

    assert result == "recovered"
    assert call_count == 3


def test_retry_raises_after_max_attempts():
    call_count = 0

    @retry(max_attempts=3, backoff_base=0, retryable_exceptions=(ConnectionError,))
    def always_fail():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("always")

    with patch("sheetpipe.retry.time.sleep"):
        with pytest.raises(ConnectionError, match="always"):
            always_fail()

    assert call_count == 3


def test_retry_does_not_catch_non_retryable_exception():
    call_count = 0

    @retry(max_attempts=3, backoff_base=0, retryable_exceptions=(ConnectionError,))
    def raise_value_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("not retryable")

    with pytest.raises(ValueError, match="not retryable"):
        raise_value_error()

    assert call_count == 1


def test_retry_backoff_sleep_is_called_with_increasing_delays():
    @retry(max_attempts=3, backoff_base=1.0, backoff_multiplier=2.0,
           retryable_exceptions=(TimeoutError,))
    def always_timeout():
        raise TimeoutError("slow")

    sleep_calls = []
    with patch("sheetpipe.retry.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
        with pytest.raises(TimeoutError):
            always_timeout()

    assert sleep_calls == [1.0, 2.0]


# ---------------------------------------------------------------------------
# with_retry functional interface
# ---------------------------------------------------------------------------

def test_with_retry_success():
    mock_fn = MagicMock(return_value=42)
    result = with_retry(mock_fn, max_attempts=2, backoff_base=0)
    assert result == 42
    mock_fn.assert_called_once()


def test_with_retry_retries_and_succeeds():
    results = [ConnectionError("x"), ConnectionError("x"), "done"]
    mock_fn = MagicMock(side_effect=results)

    with patch("sheetpipe.retry.time.sleep"):
        result = with_retry(
            mock_fn,
            max_attempts=3,
            backoff_base=0,
            retryable_exceptions=(ConnectionError,),
        )

    assert result == "done"
    assert mock_fn.call_count == 3
