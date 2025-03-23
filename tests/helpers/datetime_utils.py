"""
DateTime utilities for tests.

This module provides helper functions to create properly timezone-aware
datetime objects that comply with ADR-011 requirements.
"""

from datetime import datetime, timedelta, timezone


def utc_now():
    """
    Get current UTC time with timezone information.

    Returns:
        datetime: Current time with UTC timezone
    """
    return datetime.now(timezone.utc)


def utc_datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    """
    Create a UTC-aware datetime object.

    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)
        microsecond: Microsecond (0-999999)

    Returns:
        datetime: UTC-aware datetime object
    """
    return datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc
    )


def days_from_now(days):
    """
    Get datetime n days from now, with UTC timezone.

    Args:
        days: Number of days in the future (can be negative for past)

    Returns:
        datetime: UTC-aware datetime object
    """
    return utc_now() + timedelta(days=days)


def days_ago(days):
    """
    Get datetime n days ago, with UTC timezone.

    Args:
        days: Number of days in the past (can be negative for future)

    Returns:
        datetime: UTC-aware datetime object
    """
    return utc_now() - timedelta(days=days)


def first_day_of_month(dt=None):
    """
    Get first day of the month for a given datetime (defaults to now).

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for first day of month
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, 1)


def last_day_of_month(dt=None):
    """
    Get last day of the month for a given datetime (defaults to now).

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for last day of month
    """
    dt = dt or utc_now()
    # Simple approach - go to next month's first day, then subtract one day
    if dt.month == 12:
        next_month = utc_datetime(dt.year + 1, 1, 1)
    else:
        next_month = utc_datetime(dt.year, dt.month + 1, 1)
    return next_month - timedelta(days=1)


def ensure_utc(dt):
    """
    Ensure a datetime is UTC-aware.

    If naive, assumes it's already UTC time and adds timezone.
    If timezone-aware but not UTC, converts to UTC.

    Args:
        dt: Datetime object to ensure has UTC timezone

    Returns:
        datetime: UTC-aware datetime object
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        return dt.astimezone(timezone.utc)
    return dt


def utc_datetime_from_str(datetime_str, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Parse a string into a UTC-aware datetime.

    Args:
        datetime_str: String to parse
        format_str: Format string for parsing

    Returns:
        datetime: UTC-aware datetime object
    """
    dt = datetime.strptime(datetime_str, format_str)
    return dt.replace(tzinfo=timezone.utc)
