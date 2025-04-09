"""
Tests for datetime conversion functions in the datetime_utils module.

This module contains tests for functions that convert between different datetime representations.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from src.utils.datetime_utils import (
    ensure_utc,
    normalize_db_date,
    utc_datetime_from_str,
    naive_utc_datetime_from_str,
)


def test_ensure_utc_with_naive():
    """Test ensure_utc correctly handles naive datetime."""
    naive = datetime(2025, 3, 15, 14, 30)
    aware = ensure_utc(naive)

    assert naive.tzinfo is None
    assert aware.tzinfo == timezone.utc
    # Time should be unchanged
    assert aware.year == naive.year
    assert aware.month == naive.month
    assert aware.day == naive.day
    assert aware.hour == naive.hour
    assert aware.minute == naive.minute


def test_ensure_utc_with_different_timezone():
    """Test ensure_utc correctly enforces ADR-011 timezone requirements."""
    # Create a datetime with Eastern Time (UTC-5) - should be rejected
    eastern = timezone(timedelta(hours=-5))
    eastern_time = datetime(2025, 3, 15, 14, 30, tzinfo=eastern)

    # Should raise ValueError for non-UTC timezone
    with pytest.raises(ValueError) as exc_info:
        ensure_utc(eastern_time)
    assert "violates ADR-011" in str(exc_info.value)

    # Test with timezone that crosses day boundary - should be rejected
    far_east = timezone(timedelta(hours=10))  # UTC+10
    far_east_time = datetime(2025, 3, 15, 20, 0, tzinfo=far_east)

    # Should raise ValueError for non-UTC timezone
    with pytest.raises(ValueError) as exc_info:
        ensure_utc(far_east_time)
    assert "violates ADR-011" in str(exc_info.value)


def test_ensure_utc_with_utc_and_naive():
    """Test ensure_utc correctly handles UTC and naive datetimes (ADR-011 compliant)."""
    # Test with naive datetime
    naive_dt = datetime(2025, 3, 15, 14, 30)
    utc_dt = ensure_utc(naive_dt)

    assert utc_dt.tzinfo == timezone.utc
    # Time should be unchanged when adding UTC to naive
    assert utc_dt.hour == naive_dt.hour
    assert utc_dt.minute == naive_dt.minute

    # Test with already UTC datetime
    from src.utils.datetime_utils import utc_datetime
    original = utc_datetime(2025, 3, 15, 14, 30)
    result = ensure_utc(original)

    # Should be the same object or at least equal
    assert result == original
    assert result.tzinfo == timezone.utc


def test_ensure_utc_with_already_utc():
    """Test ensure_utc with already UTC datetime."""
    from src.utils.datetime_utils import utc_datetime
    original = utc_datetime(2025, 3, 15, 14, 30)
    result = ensure_utc(original)

    # Should be the same object or at least equal
    assert result == original
    assert result.tzinfo == timezone.utc


def test_ensure_utc_with_none():
    """Test ensure_utc with None input returns None."""
    assert ensure_utc(None) is None


def test_ensure_utc_with_invalid_type():
    """Test ensure_utc raises TypeError with invalid input."""
    with pytest.raises(TypeError):
        ensure_utc("not a datetime")

    with pytest.raises(TypeError):
        ensure_utc(123)


def test_utc_datetime_from_str():
    """Test utc_datetime_from_str correctly parses strings."""
    # Test with default format
    dt = utc_datetime_from_str("2025-03-15 14:30:45")
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30
    assert dt.second == 45
    assert dt.microsecond == 0
    assert dt.tzinfo == timezone.utc

    # Test with custom format
    dt = utc_datetime_from_str("03/15/2025 2:30 PM", "%m/%d/%Y %I:%M %p")
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14  # 2 PM = 14:00
    assert dt.minute == 30
    assert dt.second == 0
    assert dt.microsecond == 0
    assert dt.tzinfo == timezone.utc

    # Test with invalid format
    with pytest.raises(ValueError):
        utc_datetime_from_str("not a date")


def test_naive_utc_datetime_from_str():
    """Test naive_utc_datetime_from_str correctly parses strings without timezone."""
    # Test with default format
    dt = naive_utc_datetime_from_str("2025-03-15 14:30:45")
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30
    assert dt.second == 45
    assert dt.microsecond == 0
    assert dt.tzinfo is None

    # Test with custom format
    dt = naive_utc_datetime_from_str("03/15/2025 2:30 PM", "%m/%d/%Y %I:%M %p")
    assert dt.year == 2025
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14  # 2 PM = 14:00
    assert dt.minute == 30
    assert dt.second == 0
    assert dt.microsecond == 0
    assert dt.tzinfo is None

    # Test with invalid format
    with pytest.raises(ValueError):
        naive_utc_datetime_from_str("not a date")


def test_normalize_db_date():
    """Test normalize_db_date correctly handles various input types."""
    # Test with string date (common from SQLite)
    str_date = "2025-03-15"
    result = normalize_db_date(str_date)
    assert isinstance(result, date)
    assert result.year == 2025
    assert result.month == 3
    assert result.day == 15

    # Test with alternative string formats
    formats = ["2025/03/15", "15-03-2025", "03/15/2025"]
    for format_str in formats:
        result = normalize_db_date(format_str)
        assert isinstance(result, date)
        assert result.year == 2025
        assert result.month == 3
        assert result.day == 15

    # Test with datetime object (common from PostgreSQL)
    dt = datetime(2025, 3, 15, 14, 30)
    result = normalize_db_date(dt)
    assert isinstance(result, date)
    assert result.year == 2025
    assert result.month == 3
    assert result.day == 15

    # Test with date object
    d = date(2025, 3, 15)
    result = normalize_db_date(d)
    assert result == d

    # Test with non-convertible input
    non_date = "hello world"
    result = normalize_db_date(non_date)
    assert result == non_date  # Returns original value if can't convert

    # Test with additional formats that might be used in different databases
    additional_formats = ["2025.03.15", "20250315"]
    for format_str in additional_formats:
        # These might not be parseable, but the function should handle them gracefully
        result = normalize_db_date(format_str)
        # Either it's converted to a date or returned as is
        assert isinstance(result, (date, str))
