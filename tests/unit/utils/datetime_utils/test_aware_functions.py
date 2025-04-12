"""
Tests for timezone-aware datetime functions in the datetime_utils module.

This module contains tests for functions that work with timezone-aware datetimes.
"""

from datetime import datetime, timezone

import pytest

from src.utils.datetime_utils import (
    days_ago,
    days_from_now,
    end_of_day,
    first_day_of_month,
    last_day_of_month,
    start_of_day,
    utc_datetime,
    utc_now,
)


def test_utc_now():
    """Test utc_now returns current UTC time with timezone."""
    dt = utc_now()
    # Verify it has timezone info
    assert dt.tzinfo is not None
    assert dt.tzinfo == timezone.utc
    # Verify it's within 1 second of now
    assert abs((datetime.now(timezone.utc) - dt).total_seconds()) < 1


def test_utc_datetime():
    """Test utc_datetime creates proper UTC datetime objects."""
    # Test with just date
    dt1 = utc_datetime(2025, 3, 15)
    assert dt1.year == 2025
    assert dt1.month == 3
    assert dt1.day == 15
    assert dt1.hour == 0
    assert dt1.minute == 0
    assert dt1.second == 0
    assert dt1.microsecond == 0
    assert dt1.tzinfo == timezone.utc

    # Test with date and time
    dt2 = utc_datetime(2025, 3, 15, 14, 30, 45, 123456)
    assert dt2.year == 2025
    assert dt2.month == 3
    assert dt2.day == 15
    assert dt2.hour == 14
    assert dt2.minute == 30
    assert dt2.second == 45
    assert dt2.microsecond == 123456
    assert dt2.tzinfo == timezone.utc

    # Test with invalid date should raise
    with pytest.raises(ValueError):
        utc_datetime(2025, 2, 30)  # Invalid date - February 30


def test_days_from_now():
    """Test days_from_now returns correct future/past dates."""
    now = utc_now()

    # Future (positive days)
    future = days_from_now(7)
    assert future.tzinfo == timezone.utc
    # Allow 1 second tolerance for test execution time
    assert abs((future - now).total_seconds() - 7 * 86400) < 1

    # Past (negative days)
    past = days_from_now(-3)
    assert past.tzinfo == timezone.utc
    # Allow 1 second tolerance for test execution time
    assert abs((now - past).total_seconds() - 3 * 86400) < 1


def test_days_ago():
    """Test days_ago returns correct past/future dates."""
    now = utc_now()

    # Past (positive days)
    past = days_ago(5)
    assert past.tzinfo == timezone.utc
    # Allow 1 second tolerance for test execution time
    assert abs((now - past).total_seconds() - 5 * 86400) < 1

    # Future (negative days)
    future = days_ago(-2)
    assert future.tzinfo == timezone.utc
    # Allow 1 second tolerance for test execution time
    assert abs((future - now).total_seconds() - 2 * 86400) < 1


def test_first_day_of_month():
    """Test first_day_of_month returns correct beginning of month date."""
    # Test with specific date
    dt = utc_datetime(2025, 3, 15, 14, 30)
    first_day = first_day_of_month(dt)

    assert first_day.year == 2025
    assert first_day.month == 3
    assert first_day.day == 1
    assert first_day.hour == 0
    assert first_day.minute == 0
    assert first_day.second == 0
    assert first_day.microsecond == 0
    assert first_day.tzinfo == timezone.utc

    # Test without parameter (uses current month)
    current = first_day_of_month()
    now = utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == 1
    assert current.hour == 0
    assert current.minute == 0
    assert current.second == 0
    assert current.microsecond == 0
    assert current.tzinfo == timezone.utc


def test_last_day_of_month():
    """Test last_day_of_month returns correct end of month date."""
    # Test for months with different days

    # January (31 days)
    jan = utc_datetime(2025, 1, 15)
    last_jan = last_day_of_month(jan)
    assert last_jan.year == 2025
    assert last_jan.month == 1
    assert last_jan.day == 31
    assert last_jan.tzinfo == timezone.utc

    # February non-leap year (28 days)
    feb = utc_datetime(2025, 2, 15)  # 2025 is not a leap year
    last_feb = last_day_of_month(feb)
    assert last_feb.year == 2025
    assert last_feb.month == 2
    assert last_feb.day == 28
    assert last_feb.tzinfo == timezone.utc

    # February leap year (29 days)
    feb_leap = utc_datetime(2024, 2, 15)  # 2024 is a leap year
    last_feb_leap = last_day_of_month(feb_leap)
    assert last_feb_leap.year == 2024
    assert last_feb_leap.month == 2
    assert last_feb_leap.day == 29
    assert last_feb_leap.tzinfo == timezone.utc

    # April (30 days)
    apr = utc_datetime(2025, 4, 15)
    last_apr = last_day_of_month(apr)
    assert last_apr.year == 2025
    assert last_apr.month == 4
    assert last_apr.day == 30
    assert last_apr.tzinfo == timezone.utc

    # Test without parameter (uses current month)
    current = last_day_of_month()
    now = utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.tzinfo == timezone.utc


def test_start_of_day():
    """Test start_of_day returns correct beginning of day datetime."""
    # Test with specific datetime
    dt = utc_datetime(2025, 3, 15, 14, 30, 45, 123456)
    start = start_of_day(dt)

    assert start.year == 2025
    assert start.month == 3
    assert start.day == 15
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0
    assert start.microsecond == 0
    assert start.tzinfo == timezone.utc

    # Test without parameter (uses current day)
    current = start_of_day()
    now = utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == now.day
    assert current.hour == 0
    assert current.minute == 0
    assert current.second == 0
    assert current.microsecond == 0
    assert current.tzinfo == timezone.utc


def test_end_of_day():
    """Test end_of_day returns correct end of day datetime."""
    # Test with specific datetime
    dt = utc_datetime(2025, 3, 15, 14, 30, 45, 123456)
    end = end_of_day(dt)

    assert end.year == 2025
    assert end.month == 3
    assert end.day == 15
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999
    assert end.tzinfo == timezone.utc

    # Test without parameter (uses current day)
    current = end_of_day()
    now = utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == now.day
    assert current.hour == 23
    assert current.minute == 59
    assert current.second == 59
    assert current.microsecond == 999999
    assert current.tzinfo == timezone.utc
