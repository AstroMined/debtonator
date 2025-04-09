"""
Tests for datetime comparison functions in the datetime_utils module.

This module contains tests for functions that compare datetimes and dates.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from src.utils.datetime_utils import (
    date_equals,
    date_in_collection,
    datetime_equals,
    datetime_greater_than,
    datetime_less_than,
    is_adr011_compliant,
    utc_datetime,
    utc_now,
)


def test_datetime_equals_with_same_timezone():
    """Test datetime_equals with same timezone."""
    dt1 = utc_datetime(2025, 3, 15, 14, 30)
    dt2 = utc_datetime(2025, 3, 15, 14, 30)

    assert datetime_equals(dt1, dt2)

    # With microseconds
    dt3 = utc_datetime(2025, 3, 15, 14, 30, 0, 123)
    dt4 = utc_datetime(2025, 3, 15, 14, 30, 0, 456)

    assert not datetime_equals(dt3, dt4)
    assert datetime_equals(dt3, dt4, ignore_microseconds=True)


def test_datetime_equals_with_different_timezone():
    """Test datetime_equals rejects non-UTC timezones per ADR-011."""
    utc_dt = utc_datetime(2025, 3, 15, 14, 30)

    # Create datetime with Eastern Time (UTC-5)
    eastern = timezone(timedelta(hours=-5))
    eastern_dt = datetime(2025, 3, 15, 9, 30, tzinfo=eastern)  # 5 hours earlier

    # Should raise ValueError for non-UTC timezone
    with pytest.raises(ValueError) as exc_info:
        datetime_equals(utc_dt, eastern_dt)
    assert "violates ADR-011" in str(exc_info.value)

    # Different non-UTC timezone should also raise
    eastern_dt_different = datetime(2025, 3, 15, 10, 30, tzinfo=eastern)
    with pytest.raises(ValueError) as exc_info:
        datetime_equals(utc_dt, eastern_dt_different)
    assert "violates ADR-011" in str(exc_info.value)


def test_datetime_equals_with_naive_and_aware():
    """Test datetime_equals with naive and timezone-aware datetimes."""
    utc_dt = utc_datetime(2025, 3, 15, 14, 30)
    naive_dt = datetime(2025, 3, 15, 14, 30)  # Same time but naive

    # Not equal by default (naive is assumed UTC but not guaranteed)
    assert datetime_equals(utc_dt, naive_dt)

    # With ignore_timezone they should be equal
    assert datetime_equals(utc_dt, naive_dt, ignore_timezone=True)


def test_datetime_equals_invalid_inputs():
    """Test datetime_equals with invalid inputs."""
    dt = utc_datetime(2025, 3, 15, 14, 30)

    with pytest.raises(TypeError):
        datetime_equals(dt, "not a datetime")

    with pytest.raises(TypeError):
        datetime_equals("not a datetime", dt)


def test_datetime_greater_than():
    """Test datetime_greater_than correctly compares datetimes per ADR-011."""
    dt1 = utc_datetime(2025, 3, 15, 14, 30)
    dt2 = utc_datetime(2025, 3, 15, 14, 0)  # Earlier
    dt3 = utc_datetime(2025, 3, 15, 15, 0)  # Later

    # Basic UTC comparisons should work
    assert datetime_greater_than(dt1, dt2)
    assert not datetime_greater_than(dt1, dt3)
    assert not datetime_greater_than(dt1, dt1)  # Equal dates

    # Different timezones should raise ValueError
    eastern = timezone(timedelta(hours=-5))
    eastern_dt = datetime(2025, 3, 15, 9, 0, tzinfo=eastern)  # 14:00 UTC

    # Should raise ValueError for non-UTC timezone
    with pytest.raises(ValueError) as exc_info:
        datetime_greater_than(dt1, eastern_dt)
    assert "violates ADR-011" in str(exc_info.value)

    # Test with naive datetime (should handle without error)
    naive_dt = datetime(2025, 3, 15, 14, 0)  # Same as dt2 but naive

    # Comparing UTC with naive
    assert datetime_greater_than(dt1, naive_dt)  # 14:30 > 14:00
    # Comparing with ignore_timezone works too
    assert datetime_greater_than(dt1, naive_dt, ignore_timezone=True)


def test_datetime_less_than():
    """Test datetime_less_than correctly compares datetimes per ADR-011."""
    dt1 = utc_datetime(2025, 3, 15, 14, 0)
    dt2 = utc_datetime(2025, 3, 15, 14, 30)  # Later
    dt3 = utc_datetime(2025, 3, 15, 13, 30)  # Earlier

    # Basic UTC comparisons should work
    assert datetime_less_than(dt1, dt2)
    assert not datetime_less_than(dt1, dt3)
    assert not datetime_less_than(dt1, dt1)  # Equal dates

    # Different timezones should raise ValueError
    eastern = timezone(timedelta(hours=-5))
    eastern_dt = datetime(2025, 3, 15, 10, 0, tzinfo=eastern)  # 15:00 UTC

    # Should raise ValueError for non-UTC timezone
    with pytest.raises(ValueError) as exc_info:
        datetime_less_than(dt1, eastern_dt)
    assert "violates ADR-011" in str(exc_info.value)

    # Test with naive datetime (should handle without error)
    naive_dt = datetime(2025, 3, 15, 14, 30)  # Same as dt2 but naive

    # Comparing UTC with naive
    assert datetime_less_than(dt1, naive_dt)  # 14:00 < 14:30
    # Comparing with ignore_timezone works too
    assert datetime_less_than(dt1, naive_dt, ignore_timezone=True)


def test_date_equals():
    """Test date_equals correctly compares dates of different types."""
    # Python date object
    py_date = date(2025, 3, 15)

    # Test against various formats
    assert date_equals(py_date, "2025-03-15")  # String
    assert date_equals(py_date, datetime(2025, 3, 15, 14, 30))  # Datetime
    assert date_equals("2025-03-15", "2025/03/15")  # Different string formats

    # Negative tests
    assert not date_equals(py_date, date(2025, 3, 16))
    assert not date_equals(py_date, "2025-03-16")

    # Invalid input still handled gracefully
    assert not date_equals(py_date, "not a date")
    assert date_equals("not a date", "not a date")  # String equality


def test_date_in_collection():
    """Test date_in_collection checks membership correctly."""
    # Collection with mixed types
    dates = [date(2025, 3, 15), "2025-03-16", datetime(2025, 3, 17, 14, 30)]

    # Check various formats
    assert date_in_collection(date(2025, 3, 15), dates)  # Date object
    assert date_in_collection("2025-03-15", dates)  # String
    assert date_in_collection(datetime(2025, 3, 15, 14, 30), dates)  # Datetime
    assert date_in_collection("2025/03/16", dates)  # Alternative format

    # Negative tests
    assert not date_in_collection(date(2025, 3, 18), dates)
    assert not date_in_collection("2025-03-18", dates)

    # Test with empty collection
    assert not date_in_collection(date(2025, 3, 15), [])


def test_is_adr011_compliant():
    """Test is_adr011_compliant checks for UTC timezone-awareness."""
    # Compliant: UTC timezone-aware
    assert is_adr011_compliant(utc_now())
    assert is_adr011_compliant(utc_datetime(2025, 3, 15))

    # Non-compliant: naive datetime
    assert not is_adr011_compliant(datetime.now())
    assert not is_adr011_compliant(datetime(2025, 3, 15))

    # Non-compliant: non-UTC timezone
    eastern = timezone(timedelta(hours=-5))
    assert not is_adr011_compliant(datetime(2025, 3, 15, tzinfo=eastern))

    # Edge case: timezone with zero offset but not UTC
    zero_offset = timezone(timedelta(0), name="CustomZero")
    dt_zero_offset = datetime(2025, 3, 15, tzinfo=zero_offset)
    # Should still be compliant since offset is zero
    assert is_adr011_compliant(dt_zero_offset)
