"""
DateTime utilities.

This module provides helper functions to create properly timezone-aware
datetime objects that comply with ADR-011 requirements, and utilities
for safely comparing datetime objects with different timezone awareness.
"""

from datetime import datetime, timedelta, timezone, date
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


def normalize_db_date(date_val):
    """
    Normalize date values returned from the database to Python date objects.
    
    Handles different database engines that may return:
    - String dates (common in SQLite)
    - Datetime objects (common in PostgreSQL)
    - Custom date types
    
    Args:
        date_val: Date value from database
        
    Returns:
        date: Python date object or original value if conversion fails
    """
    # String case (common in SQLite)
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val, "%Y-%m-%d").date()
        except ValueError:
            # Try other common formats if the standard one fails
            for fmt in ["%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(date_val, fmt).date()
                except ValueError:
                    continue
            # If all parsing attempts fail, return as is
            return date_val
    
    # Datetime case (common in PostgreSQL, MySQL)
    elif hasattr(date_val, 'date') and callable(getattr(date_val, 'date')):
        return date_val.date()
    
    # Already a date
    elif isinstance(date_val, date) and not isinstance(date_val, datetime):
        return date_val
    
    # Other cases, just return as is
    return date_val


def date_equals(date1, date2):
    """
    Safely compare two date objects, handling potential type differences.
    
    This function handles comparison between date objects that might come
    from different sources (e.g., database query results vs. Python date objects).
    
    Args:
        date1: First date (can be date, datetime, or string)
        date2: Second date (can be date, datetime, or string)
        
    Returns:
        bool: True if dates are equal
    """
    # Normalize both dates
    date1 = normalize_db_date(date1)
    date2 = normalize_db_date(date2)
    
    # If both are dates now, do a direct comparison
    if isinstance(date1, date) and isinstance(date2, date):
        return date1 == date2
    
    # Fallback to string comparison for any values that couldn't be converted
    str1 = date1 if isinstance(date1, str) else str(date1)
    str2 = date2 if isinstance(date2, str) else str(date2)
    
    return str1 == str2


def date_in_collection(target_date, date_collection):
    """
    Check if a date exists in a collection of dates.
    
    Handles type differences and ensures reliable comparison.
    
    Args:
        target_date: Date to check for (can be date, datetime, or string)
        date_collection: Collection of dates to check against
        
    Returns:
        bool: True if the date exists in the collection
    """
    # Normalize target date
    normalized_target = normalize_db_date(target_date)
    
    for d in date_collection:
        if date_equals(normalized_target, d):
            return True
    return False


def start_of_day(dt=None):
    """
    Get start of day (00:00:00) for a given datetime.
    
    Args:
        dt: Input datetime (defaults to now if None)
        
    Returns:
        datetime: UTC-aware datetime for start of day (00:00:00)
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day)


def end_of_day(dt=None):
    """
    Get end of day (23:59:59.999999) for a given datetime.
    
    Args:
        dt: Input datetime (defaults to now if None)
        
    Returns:
        datetime: UTC-aware datetime for end of day (23:59:59.999999)
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)


def date_range(start_date, end_date):
    """
    Generate a list of dates within a range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        list: List of UTC-aware datetimes, one for each day in the range
    """
    current = start_of_day(start_date)
    end = start_of_day(end_date)
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates
