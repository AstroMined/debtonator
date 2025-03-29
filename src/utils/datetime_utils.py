"""
DateTime Utilities

This module provides comprehensive datetime handling utilities that comply with
ADR-011 requirements for datetime standardization. Functions are organized by purpose
and provide consistent timezone handling.

IMPORTANT: Per ADR-011, all datetimes in the database are stored as naive datetimes
that semantically represent UTC time, while all business logic uses timezone-aware
UTC datetimes.

Key function categories:
- Creation: Functions that create new datetime objects
- Conversion: Functions that convert between different datetime representations
- Comparison: Functions for safely comparing datetimes
- Range Operations: Functions for handling date ranges and boundaries
- Database Compatibility: Functions for handling database-specific datetime issues
"""

import calendar
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Collection, List, Optional, TypeVar, Union, overload

# Type definitions for improved type hinting
DateType = TypeVar("DateType", datetime, date, str)


#######################
# CREATION FUNCTIONS #
#######################


def utc_now() -> datetime:
    """
    Get current UTC time with timezone information.

    Returns:
        datetime: Current time with UTC timezone

    Example:
        >>> current_time = utc_now()
        >>> print(current_time.tzinfo)  # timezone.utc
    """
    return datetime.now(timezone.utc)


def utc_datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
) -> datetime:
    """
    Create a UTC-aware datetime object.

    Args:
        year: Year (full 4-digit year)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        second: Second (0-59)
        microsecond: Microsecond (0-999999)

    Returns:
        datetime: UTC-aware datetime object

    Raises:
        ValueError: If any parameter is out of range

    Example:
        >>> # Create datetime for January 15, 2025 at 2:30 PM UTC
        >>> dt = utc_datetime(2025, 1, 15, 14, 30)
        >>> print(dt.isoformat())  # 2025-01-15T14:30:00+00:00
    """
    return datetime(
        year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc
    )


def naive_utc_now() -> datetime:
    """
    Returns a naive datetime representing the current UTC time.

    This function ensures that we drop any tzinfo before storing in the DB,
    while semantically representing UTC time. Use this for SQLAlchemy model
    default values as required by ADR-011.

    Returns:
        datetime: A naive datetime containing the current UTC time

    Example:
        >>> # For SQLAlchemy model columns
        >>> created_at = Column(DateTime(), default=naive_utc_now)
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def naive_utc_from_date(
    year: int, month: int, day: int, time_of_day: Optional[time] = None
) -> datetime:
    """
    Creates a naive UTC datetime from date components.

    This function is useful for creating datetime objects that are stored
    in the database (which requires naive datetimes per ADR-011). The resulting
    datetime semantically represents UTC time but without timezone information.

    Args:
        year: Full year (e.g., 2025)
        month: Month number (1-12)
        day: Day of month (1-31)
        time_of_day: Optional time component. If None, midnight (00:00:00) is used

    Returns:
        datetime: Naive datetime that semantically represents UTC

    Raises:
        ValueError: If the date components are invalid

    Example:
        >>> # Create date for bill due on 15th
        >>> due_date = naive_utc_from_date(2025, 3, 15)
        >>> # Create date for payment scheduled at 2pm
        >>> schedule_date = naive_utc_from_date(2025, 3, 15, time(14, 0))
    """
    if time_of_day is None:
        time_of_day = time(0, 0)  # Midnight

    # Create timezone-aware UTC datetime
    aware = datetime.combine(
        datetime(year, month, day).date(), time_of_day, tzinfo=timezone.utc
    )

    # Convert to naive
    return aware.replace(tzinfo=None)


def days_from_now(days: int) -> datetime:
    """
    Get datetime n days from now, with UTC timezone.

    Args:
        days: Number of days in the future (can be negative for past)

    Returns:
        datetime: UTC-aware datetime object

    Example:
        >>> # Get datetime for one week from now
        >>> next_week = days_from_now(7)
        >>> # Get datetime for three days ago
        >>> three_days_ago = days_from_now(-3)
    """
    return utc_now() + timedelta(days=days)


def days_ago(days: int) -> datetime:
    """
    Get datetime n days ago, with UTC timezone.

    Args:
        days: Number of days in the past (can be negative for future)

    Returns:
        datetime: UTC-aware datetime object

    Example:
        >>> # Get datetime for one week ago
        >>> last_week = days_ago(7)
        >>> # Get datetime for three days in the future (negative past = future)
        >>> three_days_future = days_ago(-3)
    """
    return utc_now() - timedelta(days=days)


def first_day_of_month(dt: Optional[datetime] = None) -> datetime:
    """
    Get first day of the month for a given datetime (defaults to now).

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for first day of month at 00:00:00

    Example:
        >>> # Get first day of current month
        >>> month_start = first_day_of_month()
        >>> # Get first day of specific month
        >>> march_start = first_day_of_month(utc_datetime(2025, 3, 15))
        >>> print(march_start.isoformat())  # 2025-03-01T00:00:00+00:00
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, 1)


def last_day_of_month(dt: Optional[datetime] = None) -> datetime:
    """
    Get last day of the month for a given datetime (defaults to now).

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for last day of month at 00:00:00

    Example:
        >>> # Get last day of current month
        >>> month_end = last_day_of_month()
        >>> # Get last day of February 2024 (leap year)
        >>> feb_end = last_day_of_month(utc_datetime(2024, 2, 15))
        >>> print(feb_end.day)  # 29
    """
    dt = dt or utc_now()
    # Calculate the last day using calendar
    _, last_day = calendar.monthrange(dt.year, dt.month)
    return utc_datetime(dt.year, dt.month, last_day)


def start_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get start of day (00:00:00) for a given datetime.

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for start of day (00:00:00)

    Example:
        >>> # Get start of today
        >>> today_start = start_of_day()
        >>>
        >>> # Get start of specific date
        >>> march_1_start = start_of_day(utc_datetime(2025, 3, 1))
        >>>
        >>> # Use in a repository query
        >>> start = start_of_day(start_date)
        >>> end = end_of_day(end_date)
        >>> query = select(Entity).where(
        >>>     Entity.created_at.between(start, end)
        >>> )
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day)


def end_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get end of day (23:59:59.999999) for a given datetime.

    Args:
        dt: Input datetime (defaults to now if None)

    Returns:
        datetime: UTC-aware datetime for end of day (23:59:59.999999)

    Example:
        >>> # Get end of today
        >>> today_end = end_of_day()
        >>>
        >>> # Inclusive date range query (per ADR-011)
        >>> start = start_of_day(start_date)
        >>> end = end_of_day(end_date)
        >>> query = select(Entity).where(
        >>>     and_(
        >>>         Entity.created_at >= start,
        >>>         Entity.created_at <= end  # Note: <= for inclusive range
        >>>     )
        >>> )
    """
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)


#########################
# CONVERSION FUNCTIONS #
#########################


@overload
def ensure_utc(dt: datetime) -> datetime: ...


@overload
def ensure_utc(dt: None) -> None: ...


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensure a datetime is UTC-aware, enforcing ADR-011 compliance.

    Per ADR-011, all datetimes must either be:
    1. Naive (assumed to represent UTC time, typically from database)
    2. Timezone-aware with UTC timezone

    This function:
    - Adds UTC timezone to naive datetimes (assumes they represent UTC time)
    - Validates that timezone-aware datetimes are using UTC
    - Rejects non-UTC timezone-aware datetimes as non-compliant

    Args:
        dt: Datetime object to ensure has UTC timezone
            If None, returns None

    Returns:
        Optional[datetime]: UTC-aware datetime object or None

    Raises:
        TypeError: If dt is not a datetime object or None
        ValueError: If dt has a non-UTC timezone (ADR-011 violation)

    Example:
        >>> # Convert naive datetime to UTC-aware
        >>> naive_dt = datetime(2025, 3, 15, 14, 30)
        >>> utc_dt = ensure_utc(naive_dt)
        >>> print(utc_dt.tzinfo)  # timezone.utc
        >>>
        >>> # Error on non-UTC timezone
        >>> eastern = timezone(timedelta(hours=-5))
        >>> eastern_dt = datetime(2025, 3, 15, 14, 30, tzinfo=eastern)
        >>> try:
        >>>     utc_dt = ensure_utc(eastern_dt)
        >>> except ValueError as e:
        >>>     print(str(e))  # "Datetime has non-UTC timezone: [...]"
    """
    if dt is None:
        return None

    if not isinstance(dt, datetime):
        raise TypeError(f"Expected datetime object, got {type(dt).__name__}")

    if dt.tzinfo is None:
        # Add UTC timezone to naive datetime (assumes it represents UTC time)
        return dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        # Reject non-UTC timezone-aware datetimes
        if dt.utcoffset() != timedelta(0):
            raise ValueError(
                f"Datetime has non-UTC timezone: {dt}. "
                "This violates ADR-011 which requires all datetimes to be either "
                "naive (from DB) or timezone-aware with UTC."
            )
        # If tzinfo is different but offset is 0, normalize to standard UTC
        return dt.replace(tzinfo=timezone.utc)

    # Already UTC
    return dt


def utc_datetime_from_str(
    datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    """
    Parse a string into a UTC-aware datetime.

    Args:
        datetime_str: String to parse
        format_str: Format string for parsing (following datetime.strptime conventions)

    Returns:
        datetime: UTC-aware datetime object

    Raises:
        ValueError: If the string cannot be parsed with the given format

    Example:
        >>> # Parse ISO format string
        >>> dt = utc_datetime_from_str("2025-03-15 14:30:00")
        >>> # Parse custom format
        >>> dt = utc_datetime_from_str("03/15/2025 2:30 PM", "%m/%d/%Y %I:%M %p")
    """
    try:
        dt = datetime.strptime(datetime_str, format_str)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(
            f"Could not parse '{datetime_str}' with format '{format_str}': {e}"
        )


def normalize_db_date(date_val: Any) -> Union[date, Any]:
    """
    Normalize date values returned from the database to Python date objects.

    Handles different database engines that may return:
    - String dates (common in SQLite)
    - Datetime objects (common in PostgreSQL)
    - Custom date types

    Args:
        date_val: Date value from database (any type)

    Returns:
        date: Python date object if conversion successful
        Any: Original value if conversion fails

    Example:
        >>> # SQLite might return dates as strings
        >>> sqlite_date = "2025-03-15"
        >>> py_date = normalize_db_date(sqlite_date)
        >>> print(type(py_date))  # <class 'datetime.date'>
        >>>
        >>> # PostgreSQL returns datetime objects
        >>> pg_date = datetime(2025, 3, 15)
        >>> py_date = normalize_db_date(pg_date)
        >>> print(type(py_date))  # <class 'datetime.date'>
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
    elif hasattr(date_val, "date") and callable(getattr(date_val, "date")):
        return date_val.date()

    # Already a date
    elif isinstance(date_val, date) and not isinstance(date_val, datetime):
        return date_val

    # Other cases, just return as is
    return date_val


#########################
# COMPARISON FUNCTIONS #
#########################


def datetime_equals(
    dt1: datetime,
    dt2: datetime,
    ignore_timezone: bool = False,
    ignore_microseconds: bool = False,
) -> bool:
    """
    Safely compare two datetimes for equality, following ADR-011 requirements.

    Per ADR-011, all datetimes should either be:
    1. Naive (assumed to represent UTC time, typically from database)
    2. Timezone-aware with UTC timezone

    Args:
        dt1: First datetime
        dt2: Second datetime
        ignore_timezone: If True, treats naive datetimes and UTC-aware datetimes equally,
                        useful for comparing DB values (naive) with application values (UTC-aware)
        ignore_microseconds: If True, ignore microsecond precision in comparison

    Returns:
        bool: True if datetimes are equal considering the parameters

    Raises:
        TypeError: If dt1 or dt2 is not a datetime object
        ValueError: If any datetime has a non-UTC timezone (ADR-011 violation)

    Example:
        >>> # Compare UTC-aware datetime with naive datetime
        >>> dt1 = utc_datetime(2025, 3, 15, 14, 30)
        >>> dt2 = datetime(2025, 3, 15, 14, 30)  # naive, assumed UTC from DB
        >>> print(datetime_equals(dt1, dt2, ignore_timezone=True))  # True
        >>>
        >>> # Ignoring microseconds
        >>> dt3 = utc_datetime(2025, 3, 15, 14, 30, 0, 123)
        >>> dt4 = utc_datetime(2025, 3, 15, 14, 30, 0, 456)
        >>> print(datetime_equals(dt3, dt4, ignore_microseconds=True))  # True
    """
    if not isinstance(dt1, datetime) or not isinstance(dt2, datetime):
        raise TypeError("Both arguments must be datetime objects")

    # Check for non-UTC timezones (ADR-011 violation)
    # A datetime must either be naive (no timezone) or UTC timezone
    for dt in [dt1, dt2]:
        if dt.tzinfo is not None and dt.tzinfo != timezone.utc:
            if dt.utcoffset() != timedelta(0):
                raise ValueError(
                    f"Datetime has non-UTC timezone: {dt}. "
                    "This violates ADR-011 which requires all datetimes to be either "
                    "naive (from DB) or timezone-aware with UTC."
                )

    # Make copies to avoid modifying the originals
    dt1_copy = dt1
    dt2_copy = dt2

    if ignore_timezone:
        # For ignore_timezone, we just strip the timezone info
        # Used when comparing DB datetimes (naive) with application datetimes (UTC)
        dt1_copy = dt1.replace(tzinfo=None)
        dt2_copy = dt2.replace(tzinfo=None)
    else:
        # For timezone-aware comparisons, convert naive to UTC aware
        if dt1_copy.tzinfo is None:
            dt1_copy = dt1_copy.replace(tzinfo=timezone.utc)
        if dt2_copy.tzinfo is None:
            dt2_copy = dt2_copy.replace(tzinfo=timezone.utc)

    if ignore_microseconds:
        dt1_copy = dt1_copy.replace(microsecond=0)
        dt2_copy = dt2_copy.replace(microsecond=0)

    return dt1_copy == dt2_copy


def datetime_greater_than(
    dt1: datetime, dt2: datetime, ignore_timezone: bool = False
) -> bool:
    """
    Safely compare if dt1 > dt2, following ADR-011 requirements.

    Per ADR-011, all datetimes should either be:
    1. Naive (assumed to represent UTC time, typically from database)
    2. Timezone-aware with UTC timezone

    Args:
        dt1: First datetime
        dt2: Second datetime
        ignore_timezone: If True, treats naive datetimes and UTC-aware datetimes equally,
                        useful for comparing DB values (naive) with application values (UTC-aware)

    Returns:
        bool: True if dt1 > dt2 considering the parameters

    Raises:
        TypeError: If dt1 or dt2 is not a datetime object
        ValueError: If any datetime has a non-UTC timezone (ADR-011 violation)

    Example:
        >>> # Comparing UTC-aware datetimes
        >>> dt1 = utc_datetime(2025, 3, 15, 14, 30)
        >>> dt2 = utc_datetime(2025, 3, 15, 14, 0)
        >>> print(datetime_greater_than(dt1, dt2))  # True
        >>>
        >>> # Comparing with naive datetime (from DB)
        >>> naive_dt = datetime(2025, 3, 15, 14, 0)  # naive
        >>> print(datetime_greater_than(dt1, naive_dt))  # True
    """
    if not isinstance(dt1, datetime) or not isinstance(dt2, datetime):
        raise TypeError("Both arguments must be datetime objects")

    # Check for non-UTC timezones (ADR-011 violation)
    # A datetime must either be naive (no timezone) or UTC timezone
    for dt in [dt1, dt2]:
        if dt.tzinfo is not None and dt.tzinfo != timezone.utc:
            if dt.utcoffset() != timedelta(0):
                raise ValueError(
                    f"Datetime has non-UTC timezone: {dt}. "
                    "This violates ADR-011 which requires all datetimes to be either "
                    "naive (from DB) or timezone-aware with UTC."
                )

    # Make copies to avoid modifying the originals
    dt1_copy = dt1
    dt2_copy = dt2

    if ignore_timezone:
        # For ignore_timezone, we just strip the timezone info
        # Used when comparing DB datetimes (naive) with application datetimes (UTC)
        dt1_copy = dt1.replace(tzinfo=None)
        dt2_copy = dt2.replace(tzinfo=None)
    else:
        # For timezone-aware comparisons, convert naive to UTC aware
        if dt1_copy.tzinfo is None:
            dt1_copy = dt1_copy.replace(tzinfo=timezone.utc)
        if dt2_copy.tzinfo is None:
            dt2_copy = dt2_copy.replace(tzinfo=timezone.utc)

    return dt1_copy > dt2_copy


def date_equals(date1: Any, date2: Any) -> bool:
    """
    Safely compare two date objects, handling potential type differences.

    This function handles comparison between date objects that might come
    from different sources (e.g., database query results vs. Python date objects).

    Args:
        date1: First date (can be date, datetime, or string)
        date2: Second date (can be date, datetime, or string)

    Returns:
        bool: True if dates are equal

    Example:
        >>> # Compare dates from different sources
        >>> db_date = "2025-03-15"  # From SQLite
        >>> py_date = date(2025, 3, 15)  # Python object
        >>> print(date_equals(db_date, py_date))  # True
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


def date_in_collection(target_date: Any, date_collection: Collection[Any]) -> bool:
    """
    Check if a date exists in a collection of dates.

    Handles type differences and ensures reliable comparison.

    Args:
        target_date: Date to check for (can be date, datetime, or string)
        date_collection: Collection of dates to check against

    Returns:
        bool: True if the date exists in the collection

    Example:
        >>> # Check if a date exists in a list of dates
        >>> dates = [date(2025, 3, 15), "2025-03-16", datetime(2025, 3, 17)]
        >>> print(date_in_collection("2025-03-15", dates))  # True
        >>> print(date_in_collection(date(2025, 3, 18), dates))  # False
    """
    # Normalize target date
    normalized_target = normalize_db_date(target_date)

    for d in date_collection:
        if date_equals(normalized_target, d):
            return True
    return False


def is_adr011_compliant(dt: datetime) -> bool:
    """
    Check if a datetime is ADR-011 compliant (UTC timezone-aware).

    Used to validate that a datetime follows the project's datetime standard,
    requiring timezone-aware UTC datetimes for business logic.

    Args:
        dt: Datetime to check

    Returns:
        bool: True if the datetime has UTC timezone info (offset zero)

    Example:
        >>> naive_dt = datetime.now()
        >>> print(is_adr011_compliant(naive_dt))  # False
        >>> utc_dt = utc_now()
        >>> print(is_adr011_compliant(utc_dt))  # True
    """
    return (
        dt.tzinfo is not None
        and dt.utcoffset() is not None
        and dt.utcoffset().total_seconds() == 0
    )


#######################
# RANGE OPERATIONS #
#######################


def date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate a list of dates within a range.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        list: List of UTC-aware datetimes, one for each day in the range

    Raises:
        ValueError: If end_date is earlier than start_date

    Example:
        >>> # Get all days in March 2025
        >>> march_1 = utc_datetime(2025, 3, 1)
        >>> march_31 = utc_datetime(2025, 3, 31)
        >>> march_days = date_range(march_1, march_31)
        >>> print(len(march_days))  # 31
    """
    if end_date < start_date:
        raise ValueError("End date must be greater than or equal to start date")

    current = start_of_day(start_date)
    end = start_of_day(end_date)
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def safe_end_date(today: datetime, days: int) -> datetime:
    """
    Calculate end date safely handling month transitions.

    This function prevents "day out of range" errors when adding days that cross
    into months with fewer days. It properly handles cases such as adding 3 days
    to January 30 to get February 28 (in non-leap years) instead of causing an error.

    Args:
        today: Starting date
        days: Number of days to add

    Returns:
        datetime: End date with time set to end of day (23:59:59.999999)

    Example:
        >>> # Handle adding days that cross month boundaries
        >>> jan_30 = utc_datetime(2025, 1, 30)
        >>> # Adding 3 days would normally be Feb 2, but in calendar math
        >>> # this should be capped at Feb 28 (last day of month)
        >>> feb_end = safe_end_date(jan_30, 3)
        >>> print(feb_end.day)  # 28 (last day of February 2025)
    """
    # Get the timezone from the original date
    tzinfo = today.tzinfo

    # Handle the special case for month transitions
    # First, get the day of the month from the start date
    start_day = today.day

    # Add the days to get to the target date
    target_date = today + timedelta(days=days)

    # Check if we've crossed a month boundary and the original day
    # is near the end of the month (suggesting potential issues)
    if today.month != target_date.month and start_day > 28:
        # Get the number of days in the target month
        _, last_day = calendar.monthrange(target_date.year, target_date.month)

        # If trying to add days would exceed the last day of the month,
        # cap it at the last day of the target month
        if start_day > last_day:
            return datetime(
                target_date.year,
                target_date.month,
                last_day,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999,
                tzinfo=tzinfo,
            )

    # Standard case: set to end of the calculated day
    return datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
        tzinfo=tzinfo,
    )


def is_month_boundary(dt1: datetime, dt2: datetime) -> bool:
    """
    Check if two datetimes cross a month boundary.

    This is useful for detecting when date arithmetic crosses month boundaries,
    which might require special handling in reporting or calculations.

    Args:
        dt1: First datetime
        dt2: Second datetime

    Returns:
        bool: True if the datetimes have different months

    Example:
        >>> dt1 = utc_datetime(2025, 1, 31)
        >>> dt2 = utc_datetime(2025, 2, 1)
        >>> print(is_month_boundary(dt1, dt2))  # True
        >>>
        >>> dt3 = utc_datetime(2025, 1, 15)
        >>> dt4 = utc_datetime(2025, 1, 20)
        >>> print(is_month_boundary(dt3, dt4))  # False
    """
    return dt1.month != dt2.month or dt1.year != dt2.year
