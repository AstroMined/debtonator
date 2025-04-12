"""
Tests for naive datetime functions in the datetime_utils module.

This module contains tests for functions that work with naive datetimes (without timezone).
"""

from datetime import date, datetime, time, timezone

import pytest

from src.utils.datetime_utils import (
    naive_date_range,
    naive_days_ago,
    naive_days_from_now,
    naive_end_of_day,
    naive_first_day_of_month,
    naive_last_day_of_month,
    naive_safe_end_date,
    naive_start_of_day,
    naive_utc_datetime_from_str,
    naive_utc_from_date,
    naive_utc_now,
)


def test_naive_utc_now():
    """Test naive_utc_now returns current time without timezone."""
    dt = naive_utc_now()
    # Verify it has no timezone info
    assert dt.tzinfo is None
    # Verify it's within 1 second of now in UTC
    naive_now = datetime.now(timezone.utc).replace(tzinfo=None)
    assert abs((naive_now - dt).total_seconds()) < 1


def test_naive_utc_from_date():
    """Test naive_utc_from_date creates proper naive datetime from components."""
    # Test with just date (midnight)
    dt1 = naive_utc_from_date(2025, 3, 15)
    assert dt1.year == 2025
    assert dt1.month == 3
    assert dt1.day == 15
    assert dt1.hour == 0
    assert dt1.minute == 0
    assert dt1.second == 0
    assert dt1.microsecond == 0
    assert dt1.tzinfo is None

    # Test with custom time
    custom_time = time(14, 30, 45, 123456)
    dt2 = naive_utc_from_date(2025, 3, 15, custom_time)
    assert dt2.year == 2025
    assert dt2.month == 3
    assert dt2.day == 15
    assert dt2.hour == 14
    assert dt2.minute == 30
    assert dt2.second == 45
    assert dt2.microsecond == 123456
    assert dt2.tzinfo is None

    # Test with invalid date should raise
    with pytest.raises(ValueError):
        naive_utc_from_date(2025, 2, 30)  # Invalid date - February 30


def test_naive_days_from_now():
    """Test naive_days_from_now returns correct future/past dates without timezone."""
    now = naive_utc_now()

    # Future (positive days)
    future = naive_days_from_now(7)
    assert future.tzinfo is None
    # Allow 1 second tolerance for test execution time
    assert abs((future - now).total_seconds() - 7 * 86400) < 1

    # Past (negative days)
    past = naive_days_from_now(-3)
    assert past.tzinfo is None
    # Allow 1 second tolerance for test execution time
    assert abs((now - past).total_seconds() - 3 * 86400) < 1


def test_naive_days_ago():
    """Test naive_days_ago returns correct past/future dates without timezone."""
    now = naive_utc_now()

    # Past (positive days)
    past = naive_days_ago(5)
    assert past.tzinfo is None
    # Allow 1 second tolerance for test execution time
    assert abs((now - past).total_seconds() - 5 * 86400) < 1

    # Future (negative days)
    future = naive_days_ago(-2)
    assert future.tzinfo is None
    # Allow 1 second tolerance for test execution time
    assert abs((future - now).total_seconds() - 2 * 86400) < 1


def test_naive_first_day_of_month():
    """Test naive_first_day_of_month returns correct beginning of month date without timezone."""
    # Test with specific date
    dt = naive_utc_from_date(2025, 3, 15)
    first_day = naive_first_day_of_month(dt)

    assert first_day.year == 2025
    assert first_day.month == 3
    assert first_day.day == 1
    assert first_day.hour == 0
    assert first_day.minute == 0
    assert first_day.second == 0
    assert first_day.microsecond == 0
    assert first_day.tzinfo is None

    # Test without parameter (uses current month)
    current = naive_first_day_of_month()
    now = naive_utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == 1
    assert current.hour == 0
    assert current.minute == 0
    assert current.second == 0
    assert current.microsecond == 0
    assert current.tzinfo is None


def test_naive_last_day_of_month():
    """Test naive_last_day_of_month returns correct end of month date without timezone."""
    # Test for months with different days

    # January (31 days)
    jan = naive_utc_from_date(2025, 1, 15)
    last_jan = naive_last_day_of_month(jan)
    assert last_jan.year == 2025
    assert last_jan.month == 1
    assert last_jan.day == 31
    assert last_jan.tzinfo is None

    # February non-leap year (28 days)
    feb = naive_utc_from_date(2025, 2, 15)  # 2025 is not a leap year
    last_feb = naive_last_day_of_month(feb)
    assert last_feb.year == 2025
    assert last_feb.month == 2
    assert last_feb.day == 28
    assert last_feb.tzinfo is None

    # February leap year (29 days)
    feb_leap = naive_utc_from_date(2024, 2, 15)  # 2024 is a leap year
    last_feb_leap = naive_last_day_of_month(feb_leap)
    assert last_feb_leap.year == 2024
    assert last_feb_leap.month == 2
    assert last_feb_leap.day == 29
    assert last_feb_leap.tzinfo is None

    # April (30 days)
    apr = naive_utc_from_date(2025, 4, 15)
    last_apr = naive_last_day_of_month(apr)
    assert last_apr.year == 2025
    assert last_apr.month == 4
    assert last_apr.day == 30
    assert last_apr.tzinfo is None

    # Test without parameter (uses current month)
    current = naive_last_day_of_month()
    now = naive_utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.tzinfo is None


def test_naive_start_of_day():
    """Test naive_start_of_day returns correct beginning of day datetime without timezone."""
    # Test with specific datetime
    dt = naive_utc_from_date(2025, 3, 15, time(14, 30, 45, 123456))
    start = naive_start_of_day(dt)

    assert start.year == 2025
    assert start.month == 3
    assert start.day == 15
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0
    assert start.microsecond == 0
    assert start.tzinfo is None

    # Test without parameter (uses current day)
    current = naive_start_of_day()
    now = naive_utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == now.day
    assert current.hour == 0
    assert current.minute == 0
    assert current.second == 0
    assert current.microsecond == 0
    assert current.tzinfo is None


def test_naive_end_of_day():
    """Test naive_end_of_day returns correct end of day datetime without timezone."""
    # Test with specific datetime
    dt = naive_utc_from_date(2025, 3, 15, time(14, 30, 45, 123456))
    end = naive_end_of_day(dt)

    assert end.year == 2025
    assert end.month == 3
    assert end.day == 15
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999
    assert end.tzinfo is None

    # Test without parameter (uses current day)
    current = naive_end_of_day()
    now = naive_utc_now()
    assert current.year == now.year
    assert current.month == now.month
    assert current.day == now.day
    assert current.hour == 23
    assert current.minute == 59
    assert current.second == 59
    assert current.microsecond == 999999
    assert current.tzinfo is None


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


def test_naive_date_range():
    """Test naive_date_range generates correct list of dates without timezone."""
    # Test with single day range
    start = naive_utc_from_date(2025, 3, 15)
    end = naive_utc_from_date(2025, 3, 15)
    dates = naive_date_range(start, end)

    assert len(dates) == 1
    assert dates[0].date() == date(2025, 3, 15)
    assert dates[0].tzinfo is None

    # Test with multi-day range
    start = naive_utc_from_date(2025, 3, 15)
    end = naive_utc_from_date(2025, 3, 20)
    dates = naive_date_range(start, end)

    assert len(dates) == 6  # Inclusive range
    assert dates[0].date() == date(2025, 3, 15)
    assert dates[-1].date() == date(2025, 3, 20)
    assert all(d.tzinfo is None for d in dates)

    # Test with month boundary
    start = naive_utc_from_date(2025, 3, 30)
    end = naive_utc_from_date(2025, 4, 2)
    dates = naive_date_range(start, end)

    assert len(dates) == 4
    assert [d.date() for d in dates] == [
        date(2025, 3, 30),
        date(2025, 3, 31),
        date(2025, 4, 1),
        date(2025, 4, 2),
    ]
    assert all(d.tzinfo is None for d in dates)

    # Test with invalid range
    with pytest.raises(ValueError):
        naive_date_range(end, start)  # End before start


def test_naive_safe_end_date():
    """Test naive_safe_end_date handles month transitions correctly without timezone."""
    # Normal case within month
    start = naive_utc_from_date(2025, 3, 15)
    end = naive_safe_end_date(start, 5)

    assert end.date() == date(2025, 3, 20)
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999
    assert end.tzinfo is None

    # Month transition with day overflow
    # January 30 + 3 days would be February 32, which is invalid
    start = naive_utc_from_date(2025, 1, 30)
    end = naive_safe_end_date(start, 3)

    # Should be February 28 (end of month) since 2025 is not a leap year
    assert end.date() == date(2025, 2, 28)
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999
    assert end.tzinfo is None

    # Leap year case
    start = naive_utc_from_date(2024, 1, 30)  # 2024 is a leap year
    end = naive_safe_end_date(start, 3)

    # Should be February 29 (end of month in leap year)
    assert end.date() == date(2024, 2, 29)
    assert end.tzinfo is None
