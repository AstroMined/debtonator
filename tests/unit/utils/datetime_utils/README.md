# Datetime Utilities Tests

This directory contains unit tests for the datetime utility functions defined in `src/utils/datetime_utils/`. These tests verify the behavior of functions that handle timezone-aware and naive datetimes in accordance with ADR-011.

## ADR-011 Compliance

All datetime utilities must comply with ADR-011, which specifies:

1. All datetimes in business logic must be UTC-aware
2. All datetimes stored in the database must be naive (timezone-free)
3. Conversion between aware and naive must follow consistent patterns
4. Comparison operations must handle timezone differences correctly
5. Range operations must use consistent timezone handling

## Test File Organization

```tree
datetime_utils/
├── test_aware_functions.py      # Tests for functions that work with timezone-aware datetimes
├── test_comparison_functions.py # Tests for datetime comparison functions
├── test_conversion_functions.py # Tests for converting between aware and naive datetimes
├── test_naive_functions.py      # Tests for functions that work with naive datetimes
└── test_range_operations.py     # Tests for date range and interval operations
```

## Testing Focus Areas

### Timezone-Aware Functions

The `test_aware_functions.py` file tests functions that work with timezone-aware datetimes:

```python
def test_utc_now():
    """Test that utc_now() returns a timezone-aware datetime with UTC timezone."""
    now = utc_now()
    
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc
    
    # Test that the time is close to the current time
    system_now = datetime.now(timezone.utc)
    difference = abs((system_now - now).total_seconds())
    assert difference < 1.0  # Less than 1 second difference
```

### Timezone Conversion

The `test_conversion_functions.py` file tests functions that convert between aware and naive datetimes:

```python
def test_naive_to_aware():
    """Test converting naive datetime to timezone-aware datetime."""
    naive_dt = datetime(2023, 1, 1, 12, 0, 0)  # Naive datetime
    aware_dt = naive_to_aware(naive_dt)
    
    assert aware_dt.tzinfo is not None
    assert aware_dt.tzinfo == timezone.utc
    assert aware_dt.year == naive_dt.year
    assert aware_dt.month == naive_dt.month
    assert aware_dt.day == naive_dt.day
    assert aware_dt.hour == naive_dt.hour
    
    # Test with custom timezone
    est = timezone(timedelta(hours=-5))
    aware_est = naive_to_aware(naive_dt, tz=est)
    
    assert aware_est.tzinfo == est
    assert aware_est.hour == naive_dt.hour  # Same hour, different timezone
```

### Datetime Comparison

The `test_comparison_functions.py` file tests functions that compare datetimes with timezone awareness:

```python
def test_datetime_equals():
    """Test datetime equality comparison with timezone handling."""
    # Same time in different timezones
    utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    est = timezone(timedelta(hours=-5))
    est_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=est)
    
    # These represent the same moment in time
    assert datetime_equals(utc_dt, est_dt)
    
    # Test with naive datetimes
    naive1 = datetime(2023, 1, 1, 12, 0, 0)
    naive2 = datetime(2023, 1, 1, 12, 0, 0)
    
    assert datetime_equals(naive1, naive2)
    
    # Test mixed naive and aware with ignore_timezone
    assert datetime_equals(naive1, utc_dt, ignore_timezone=True)
    
    # Test different times
    different_dt = datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
    assert not datetime_equals(utc_dt, different_dt)
```

### Range Operations

The `test_range_operations.py` file tests functions that work with date ranges:

```python
def test_date_range_filter():
    """Test filtering datetimes by date range."""
    # Create a list of datetimes
    datetimes = [
        datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2023, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2023, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
    ]
    
    # Filter by range
    start_date = datetime(2023, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
    end_date = datetime(2023, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
    
    filtered = filter_by_date_range(datetimes, start_date, end_date)
    assert len(filtered) == 1
    assert filtered[0] == datetimes[1]  # Only Jan 15 should be included
```

### Naive Datetime Functions

The `test_naive_functions.py` file tests functions that work with naive datetimes for database operations:

```python
def test_naive_utc_now():
    """Test that naive_utc_now() returns a naive datetime."""
    now = naive_utc_now()
    
    assert now.tzinfo is None  # Should be naive
    
    # Test that the time is close to the current time
    system_now = datetime.now(timezone.utc).replace(tzinfo=None)
    difference = abs((system_now - now).total_seconds())
    assert difference < 1.0  # Less than 1 second difference
```

## Best Practices

1. **Test Both Naive and Aware Functions**: Test both types of datetime functions
2. **Test Timezone Conversion**: Verify conversions work correctly
3. **Test Edge Cases**: Include tests for DST transitions, leap years, etc.
4. **Test Comparison Logic**: Ensure comparison functions handle timezones correctly
5. **Document Usage Patterns**: Use tests to document correct usage of datetime functions
6. **Validate ADR-011 Compliance**: Ensure all tests verify compliance with ADR-011
