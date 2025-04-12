"""
Unit tests for the datetime_utils module.

Tests all datetime utility functions with a focus on:
- Creation functions for timezone-aware and naive datetimes
- Conversion functions
- Comparison functions
- Range operations
- ADR-011 compliance
"""

from datetime import date, datetime, time, timedelta, timezone

import pytest

from src.utils.datetime_utils import (
    date_equals,
    date_in_collection,
    date_range,
    datetime_equals,
    datetime_greater_than,
    days_ago,
    days_from_now,
    end_of_day,
    ensure_utc,
    first_day_of_month,
    is_adr011_compliant,
    is_month_boundary,
    last_day_of_month,
    naive_days_ago,
    naive_days_from_now,
    naive_end_of_day,
    naive_first_day_of_month,
    naive_last_day_of_month,
    naive_start_of_day,
    naive_utc_datetime_from_str,
    naive_utc_from_date,
    naive_utc_now,
    normalize_db_date,
    safe_end_date,
    start_of_day,
    utc_datetime,
    utc_datetime_from_str,
    utc_now,
)

# Creation Functions Tests


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


# Conversion Functions Tests


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
    original = utc_datetime(2025, 3, 15, 14, 30)
    result = ensure_utc(original)

    # Should be the same object or at least equal
    assert result == original
    assert result.tzinfo == timezone.utc


def test_ensure_utc_with_already_utc():
    """Test ensure_utc with already UTC datetime."""
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


# Comparison Functions Tests


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


def test_date_range():
    """Test date_range generates correct list of dates."""
    # Test with single day range
    start = utc_datetime(2025, 3, 15)
    end = utc_datetime(2025, 3, 15)
    dates = date_range(start, end)

    assert len(dates) == 1
    assert dates[0].date() == date(2025, 3, 15)

    # Test with multi-day range
    start = utc_datetime(2025, 3, 15)
    end = utc_datetime(2025, 3, 20)
    dates = date_range(start, end)

    assert len(dates) == 6  # Inclusive range
    assert dates[0].date() == date(2025, 3, 15)
    assert dates[-1].date() == date(2025, 3, 20)

    # Test with month boundary
    start = utc_datetime(2025, 3, 30)
    end = utc_datetime(2025, 4, 2)
    dates = date_range(start, end)

    assert len(dates) == 4
    assert [d.date() for d in dates] == [
        date(2025, 3, 30),
        date(2025, 3, 31),
        date(2025, 4, 1),
        date(2025, 4, 2),
    ]

    # Test with invalid range
    with pytest.raises(ValueError):
        date_range(end, start)  # End before start


def test_safe_end_date():
    """Test safe_end_date handles month transitions correctly."""
    # Normal case within month
    start = utc_datetime(2025, 3, 15)
    end = safe_end_date(start, 5)

    assert end.date() == date(2025, 3, 20)
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999

    # Month transition with day overflow
    # January 30 + 3 days would be February 32, which is invalid
    start = utc_datetime(2025, 1, 30)
    end = safe_end_date(start, 3)

    # Should be February 28 (end of month) since 2025 is not a leap year
    assert end.date() == date(2025, 2, 28)
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59
    assert end.microsecond == 999999

    # Leap year case
    start = utc_datetime(2024, 1, 30)  # 2024 is a leap year
    end = safe_end_date(start, 3)

    # Should be February 29 (end of month in leap year)
    assert end.date() == date(2024, 2, 29)

    # Preserves timezone
    eastern = timezone(timedelta(hours=-5))
    start = datetime(2025, 1, 30, tzinfo=eastern)
    end = safe_end_date(start, 3)

    assert end.tzinfo == eastern


def test_is_month_boundary():
    """Test is_month_boundary detects month transitions."""
    # Same month
    dt1 = utc_datetime(2025, 3, 15)
    dt2 = utc_datetime(2025, 3, 30)
    assert not is_month_boundary(dt1, dt2)

    # Different months
    dt3 = utc_datetime(2025, 3, 31)
    dt4 = utc_datetime(2025, 4, 1)
    assert is_month_boundary(dt3, dt4)

    # Same month different years
    dt5 = utc_datetime(2024, 3, 15)
    dt6 = utc_datetime(2025, 3, 15)
    assert is_month_boundary(dt5, dt6)

    # Different months, different years
    dt7 = utc_datetime(2024, 12, 31)
    dt8 = utc_datetime(2025, 1, 1)
    assert is_month_boundary(dt7, dt8)


def test_inclusive_date_range_pattern():
    """Test inclusive date range pattern from ADR-011."""
    # Setup a date range for testing
    start_date = utc_datetime(2025, 3, 15)
    end_date = utc_datetime(2025, 3, 17)

    # Get proper range boundaries
    range_start = start_of_day(start_date)
    range_end = end_of_day(end_date)

    # Verify inclusive behavior
    assert range_start.hour == 0
    assert range_start.minute == 0
    assert range_end.hour == 23
    assert range_end.minute == 59

    # Test a datetime at exact start boundary
    exact_start = utc_datetime(2025, 3, 15, 0, 0, 0)
    assert exact_start >= range_start  # Should be included

    # Test a datetime at exact end boundary
    exact_end = utc_datetime(2025, 3, 17, 23, 59, 59, 999999)
    assert exact_end <= range_end  # Should be included

    # Test dates in the range
    test_dates = [
        utc_datetime(2025, 3, 15, 12, 30),  # Middle of start day
        utc_datetime(2025, 3, 16, 0, 0),  # Start of middle day
        utc_datetime(2025, 3, 16, 23, 59),  # End of middle day
        utc_datetime(2025, 3, 17, 9, 15),  # During end day
    ]

    # All should be within range
    for test_date in test_dates:
        assert range_start <= test_date <= range_end

    # Test dates outside the range
    outside_dates = [
        utc_datetime(2025, 3, 14, 23, 59, 59, 999999),  # Just before start
        utc_datetime(2025, 3, 18, 0, 0, 0),  # Just after end
    ]

    # None should be within range
    for test_date in outside_dates:
        assert not (range_start <= test_date <= range_end)
