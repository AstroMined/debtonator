# UTC Datetime Compliance Guide

This guide explains how to maintain compliance with ADR-011, which requires all datetime objects to have UTC timezone information.

## New Tools for ADR-011 Compliance

Two key components have been implemented to help maintain datetime compliance:

1. **Datetime Helper Utilities**: Ready-to-use functions to create properly timezone-aware datetime objects
2. **Pytest Hooks**: Automatic detection of naive datetime usage during test runs

## Datetime Helper Utilities

Located at `tests/helpers/datetime_utils.py`, these utilities provide easy-to-use functions for creating and working with UTC datetime objects:

```python
from tests.helpers.datetime_utils import utc_now, utc_datetime, days_from_now

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

# Ensure a datetime has UTC timezone
safe_datetime = ensure_utc(some_datetime)

# Parse a string into UTC datetime
from_string = utc_datetime_from_str("2025-03-15 14:30:00")
```

## Common Replacements

Replace naive datetime usage with our helper functions:

| Instead of... | Use... |
|---------------|--------|
| `datetime.now()` | `utc_now()` |
| `datetime.utcnow()` | `utc_now()` |
| `datetime(2025, 3, 15)` | `utc_datetime(2025, 3, 15)` |
| `datetime.now() + timedelta(days=10)` | `days_from_now(10)` |
| `datetime.now() - timedelta(days=5)` | `days_ago(5)` |

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

## Next Steps

1. Run the naive datetime report to identify all instances
2. Systematically fix identified issues using the datetime helper functions
3. Consider adding these helper functions to your production code as well
4. Integrate the datetime check into your CI pipeline to prevent regressions

## Additional Resources

- Review [ADR-011](../adr/011-datetime-standardization.md) for a complete overview of datetime requirements
- See [Implementation Lessons](../active_context.md) for more context on UTC datetime handling
