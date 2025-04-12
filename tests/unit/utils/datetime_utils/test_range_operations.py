"""
Tests for datetime range operations in the datetime_utils module.

This module contains tests for functions that work with date ranges.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from src.utils.datetime_utils import (
    date_range,
    end_of_day,
    is_month_boundary,
    naive_date_range,
    safe_end_date,
    start_of_day,
    utc_datetime,
)


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

    # Edge case: same date
    dt9 = utc_datetime(2025, 3, 15)
    assert not is_month_boundary(dt9, dt9)


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


def test_date_range_with_timezone_preservation():
    """Test date_range preserves timezone information."""
    # Create dates with UTC timezone
    start = utc_datetime(2025, 3, 15)
    end = utc_datetime(2025, 3, 17)

    dates = date_range(start, end)

    # Verify all dates have UTC timezone
    assert all(d.tzinfo == timezone.utc for d in dates)

    # Create dates with a different timezone
    eastern = timezone(timedelta(hours=-5))
    start_eastern = datetime(2025, 3, 15, tzinfo=eastern)
    end_eastern = datetime(2025, 3, 17, tzinfo=eastern)

    # This should raise ValueError due to ADR-011 compliance
    with pytest.raises(ValueError):
        date_range(start_eastern, end_eastern)


def test_naive_date_range_with_no_timezone():
    """Test naive_date_range ensures no timezone information."""
    # Create dates with no timezone
    from src.utils.datetime_utils import naive_utc_from_date

    start = naive_utc_from_date(2025, 3, 15)
    end = naive_utc_from_date(2025, 3, 17)

    dates = naive_date_range(start, end)

    # Verify all dates have no timezone
    assert all(d.tzinfo is None for d in dates)

    # Create dates with UTC timezone
    start_utc = utc_datetime(2025, 3, 15)
    end_utc = utc_datetime(2025, 3, 17)

    # This should work but strip timezone
    dates_from_utc = naive_date_range(start_utc, end_utc)
    assert all(d.tzinfo is None for d in dates_from_utc)
