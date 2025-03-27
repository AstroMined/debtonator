"""
DateTime utilities.

This module provides helper functions to create properly timezone-aware
datetime objects that comply with ADR-011 requirements, and utilities
for safely comparing datetime objects with different timezone awareness.
"""

from datetime import datetime, timedelta, timezone
import calendar


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


def datetime_equals(dt1, dt2, ignore_timezone=False, ignore_microseconds=False):
    """
    Safely compare two datetimes, handling timezone differences.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        ignore_timezone: If True, only compare the time values, not timezone
        ignore_microseconds: If True, ignore microsecond precision
        
    Returns:
        bool: True if datetimes are equal considering the parameters
    """
    # Make copies to avoid modifying the originals
    dt1_copy = dt1
    dt2_copy = dt2
    
    # Normalize both to UTC-aware if either has timezone
    if dt1_copy.tzinfo is not None or dt2_copy.tzinfo is not None:
        dt1_copy = ensure_utc(dt1_copy)
        dt2_copy = ensure_utc(dt2_copy)
    
    if ignore_microseconds:
        dt1_copy = dt1_copy.replace(microsecond=0)
        dt2_copy = dt2_copy.replace(microsecond=0)
        
    if ignore_timezone:
        dt1_copy = dt1_copy.replace(tzinfo=None)
        dt2_copy = dt2_copy.replace(tzinfo=None)
        
    return dt1_copy == dt2_copy


def datetime_greater_than(dt1, dt2, ignore_timezone=False):
    """
    Safely compare if dt1 > dt2, handling timezone differences.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        ignore_timezone: If True, only compare the time values, not timezone
        
    Returns:
        bool: True if dt1 > dt2 considering the parameters
    """
    # Make copies to avoid modifying the originals
    dt1_copy = dt1
    dt2_copy = dt2
    
    # Normalize both to UTC-aware if either has timezone
    if dt1_copy.tzinfo is not None or dt2_copy.tzinfo is not None:
        dt1_copy = ensure_utc(dt1_copy)
        dt2_copy = ensure_utc(dt2_copy)
        
    if ignore_timezone:
        dt1_copy = dt1_copy.replace(tzinfo=None)
        dt2_copy = dt2_copy.replace(tzinfo=None)
        
    return dt1_copy > dt2_copy


def safe_end_date(today, days):
    """
    Calculate end date safely handling month transitions.
    
    This prevents "day out of range" errors when adding days crosses
    into months with fewer days.
    
    Args:
        today (datetime): Starting date
        days (int): Number of days to add
        
    Returns:
        datetime: End date with time set to end of day (23:59:59.999999)
    """
    
    # Get the timezone from the original date
    tzinfo = today.tzinfo
    
    # Simple case - within same month
    target_date = today + timedelta(days=days)
    
    # Check if the day would be invalid in the target month
    # (e.g., trying to create Feb 30)
    year, month = target_date.year, target_date.month
    _, last_day = calendar.monthrange(year, month)
    
    # If the day exceeds the last day of the month, cap it
    if target_date.day > last_day:
        # Use the last day of the month instead
        return datetime(year, month, last_day, 
                       hour=23, minute=59, second=59, microsecond=999999,
                       tzinfo=tzinfo)
    
    # Otherwise, use the end of the calculated day
    return datetime(target_date.year, target_date.month, target_date.day,
                  hour=23, minute=59, second=59, microsecond=999999,
                  tzinfo=tzinfo)
