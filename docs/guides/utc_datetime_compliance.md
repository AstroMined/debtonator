# UTC Datetime Compliance Guide

> **⚠️ FILE SYNCHRONIZATION NOTICE**
>
> This guide is part of a triad of files that must remain synchronized:
> - **This guide**: User-facing documentation explaining datetime standards
> - **ADR-011**: [`docs/adr/backend/011-datetime-standardization.md`] - Architectural decision record
> - **Implementation**: [`src/utils/datetime_utils.py`] - Actual utility functions
>
> When making changes to this guide, you MUST review and update the other files to maintain consistency.
> The implementation in `datetime_utils.py` is the definitive source for function behavior.

This guide explains how to maintain compliance with ADR-011, which requires all datetime objects to have UTC timezone information. It provides practical guidance on using the datetime utilities provided in the codebase.

## Core Principles from ADR-011

1. **UTC for storage**: All date/time columns in the database are treated as UTC, stored as naive datetimes.
2. **UTC for Python code**: All datetime objects in Python code must be timezone-aware with UTC timezone.
3. **Inclusive date ranges**: Date ranges include both the start and end dates.
4. **Database compatibility**: Use utility functions to handle database-specific datetime issues.

## Datetime Helper Utilities

Located at `src/utils/datetime_utils.py`, these utilities provide comprehensive functions for creating and working with UTC datetime objects. The functions are organized into categories:

### Creation Functions

```python
from src.utils.datetime_utils import utc_now, utc_datetime, days_from_now, days_ago

# Get current time with UTC timezone
now = utc_now()

# Create a specific datetime with UTC timezone
meeting_time = utc_datetime(2025, 4, 15, 14, 30)  # April 15, 2025 at 2:30 PM UTC

# Get a datetime 5 days from now
next_week = days_from_now(5)

# Get a datetime 3 days ago
last_week = days_ago(3)

# Get first day of current month
first_day = first_day_of_month()

# Get last day of current month
last_day = last_day_of_month()

# Get start of day (00:00:00)
day_start = start_of_day(some_date)

# Get end of day (23:59:59.999999)
day_end = end_of_day(some_date)

# Create a naive datetime for DB storage (no timezone info)
db_date = naive_utc_now()
```

### Conversion Functions

```python
from src.utils.datetime_utils import ensure_utc, utc_datetime_from_str, normalize_db_date

# Ensure a datetime has UTC timezone
safe_datetime = ensure_utc(some_datetime)

# Parse a string into UTC datetime
from_string = utc_datetime_from_str("2025-03-15 14:30:00")

# Normalize date values from database
db_date = normalize_db_date(date_from_query)
```

### Comparison Functions

```python
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, datetime_less_than, date_equals

# Compare datetimes for equality
if datetime_equals(dt1, dt2):
    print("Datetimes are equal")

# Compare datetimes with timezone handling
if datetime_equals(dt1, dt2, ignore_timezone=True):
    print("Semantically equal regardless of timezone info")

# Compare datetimes ignoring microseconds
if datetime_equals(dt1, dt2, ignore_microseconds=True):
    print("Equal ignoring microsecond precision")

# Compare datetimes for greater than
if datetime_greater_than(dt1, dt2):
    print("dt1 is later than dt2")

# Compare datetimes for less than
if datetime_less_than(dt1, dt2):
    print("dt1 is earlier than dt2")

# Compare dates (handles different types from different DB engines)
if date_equals(date1, date2):
    print("Dates are equal")

# Check if date exists in collection
if date_in_collection(target_date, date_collection):
    print("Date found in collection")
```

### Range Operations

```python
from src.utils.datetime_utils import date_range, safe_end_date, is_month_boundary

# Generate a list of dates within a range (inclusive)
march_days = date_range(march_1, march_31)

# Calculate end date safely handling month transitions
end_date = safe_end_date(start_date, days_to_add)

# Check if dates cross a month boundary
if is_month_boundary(dt1, dt2):
    print("Dates cross a month boundary")
```

## Common Replacements

Replace direct datetime usage with our helper functions:

| Instead of... | Use... | Notes |
|---------------|--------|-------|
| `datetime.now()` | `utc_now()` | Always timezone-aware |
| `datetime.utcnow()` | `utc_now()` | Deprecated in Python 3.12+ |
| `datetime(2025, 3, 15)` | `utc_datetime(2025, 3, 15)` | Creates with UTC timezone |
| `datetime.now() + timedelta(days=10)` | `days_from_now(10)` | Simpler and safer |
| `datetime.now() - timedelta(days=5)` | `days_ago(5)` | Simpler and safer |
| `dt.replace(hour=0, minute=0, second=0)` | `start_of_day(dt)` | Clearer intent |
| `dt.replace(hour=23, minute=59, second=59)` | `end_of_day(dt)` | Clearer intent |
| `dt1 == dt2` | `datetime_equals(dt1, dt2)` | Safer comparison |
| `dt1 > dt2` | `datetime_greater_than(dt1, dt2)` | Safer comparison |
| `dt1 < dt2` | `datetime_less_than(dt1, dt2)` | Safer comparison |

## Repository Method Patterns

When implementing repository methods that deal with date ranges, follow these patterns:

```python
async def get_by_date_range(self, account_id: int, start_date, end_date) -> List[Entity]:
    """
    Get entities within a date range.
    
    Following ADR-011, uses inclusive date range with start_of_day and end_of_day
    to ensure consistent date range handling across the application.
    """
    # Ensure proper date range bounds per ADR-011
    range_start = start_of_day(ensure_utc(start_date))
    range_end = end_of_day(ensure_utc(end_date))
    
    query = select(Entity).where(
        and_(
            Entity.account_id == account_id,
            Entity.datetime_field >= range_start,
            Entity.datetime_field <= range_end,  # Note: <= for inclusive range
        )
    )
    
    result = await self.session.execute(query)
    return result.scalars().all()
```

## Database Compatibility

Different database engines handle date values differently:

- **SQLite** often returns dates as strings (e.g., "2025-03-27")
- **PostgreSQL/MySQL** return proper datetime or date objects
- **MariaDB** may return custom date types depending on the driver

Use these functions to handle database-specific issues:

```python
# Normalize date values from database
normalized_date = normalize_db_date(date_from_query)

# Compare dates safely
if date_equals(date1, date2):
    print("Dates are equal")

# In repository methods
for item in db_results:
    # Normalize datetime values from the database
    item.transaction_date = normalize_db_date(item.transaction_date)
```

## Enforcement Mechanisms

The datetime utilities enforce ADR-011 compliance in several ways:

1. **Explicit Rejection of Non-UTC Timezones**:
   ```python
   # This will raise a ValueError
   eastern = timezone(timedelta(hours=-5))
   eastern_dt = datetime(2025, 3, 15, 14, 30, tzinfo=eastern)
   utc_dt = ensure_utc(eastern_dt)  # ValueError: Datetime has non-UTC timezone
   ```

2. **Validation in Comparison Functions**:
   ```python
   # All comparison functions validate timezone compliance
   datetime_equals(dt1, dt2)  # Validates both datetimes
   datetime_greater_than(dt1, dt2)  # Validates both datetimes
   datetime_less_than(dt1, dt2)  # Validates both datetimes
   ```

3. **Pytest Hooks**:
   The project includes pytest hooks that automatically detect naive datetime usage in tests.

## Naive Datetime Detection

To find all naive datetime usage in tests, run pytest with the `--naive-datetime-report` flag:

```bash
pytest --naive-datetime-report
```

This will:
1. Check all test functions for naive datetime usage
2. Display warnings in the console during test runs
3. Generate a comprehensive `naive_datetime_report.md` file when finished

The report contains:
- A count of all naive datetime instances
- File-by-file breakdown with line numbers
- Specific code snippets that need fixing
- Recommendations for replacing with proper UTC-aware alternatives

## Testing Best Practices

When writing tests that involve datetimes:

1. **Use the utility functions**:
   ```python
   # Instead of:
   now = datetime.now(timezone.utc)
   start_date = now - timedelta(days=22)
   
   # Use:
   current = utc_now()
   start_date = days_ago(22)
   ```

2. **Use safe comparisons**:
   ```python
   # Instead of:
   assert entry.datetime_field >= start_date
   
   # Use:
   assert datetime_greater_than(entry.datetime_field, start_date)
   ```

3. **Handle database values properly**:
   ```python
   # When comparing dates from database:
   db_date = normalize_db_date(result.date_field)
   assert date_equals(db_date, expected_date)
   ```

## Next Steps

1. Run the naive datetime report to identify all instances
2. Systematically fix identified issues using the datetime helper functions
3. Ensure all repository methods follow the recommended patterns
4. Update tests to use the safe comparison functions
5. Integrate the datetime check into your CI pipeline to prevent regressions

## Additional Resources

- Review [ADR-011](../adr/backend/011-datetime-standardization.md) for a complete overview of datetime requirements
- Explore the full implementation in [src/utils/datetime_utils.py](../../src/utils/datetime_utils.py)
- See [Implementation Lessons](../active_context.md) for more context on UTC datetime handling
