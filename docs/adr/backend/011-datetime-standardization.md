<!-- markdownlint-disable MD024 -->
# ADR-011: Datetime Standardization

> **⚠️ FILE SYNCHRONIZATION NOTICE**
>
> This ADR is part of a triad of files that must remain synchronized:
>
> - **This ADR**: Architectural decision record defining the standard
> - **User Guide**: [`docs/guides/utc_datetime_compliance.md`] - Developer documentation
> - **Implementation**: [`src/utils/datetime_utils.py`] - Actual utility functions
>
> When updating this ADR, you MUST review and update the other files to maintain consistency.
> The implementation in `datetime_utils.py` is the definitive source for function behavior.

## Status

Implemented

## Executive Summary

This ADR establishes a comprehensive datetime handling standard throughout the Debtonator platform that enforces UTC storage for all datetime values while providing specialized utilities for each architectural layer. It eliminates timezone inconsistencies by storing all timestamps as UTC, centralizing timezone validation in Pydantic schemas, simplifying database operations with naive datetimes, and providing standardized utility functions for timezone-aware business logic and naive database operations. The implementation is fully complete across all 18 models, supported by consistent patterns for inclusive date range handling, cross-database compatibility, and timezone enforcement with thorough docstrings, resulting in a reliable, maintainable datetime system with 100% test coverage.

## Context

We need consistent handling of date/time values across the application to avoid time zone–related bugs and inaccuracies. Our environment setup involves:

- **SQLite** for local development and testing
- **MariaDB** for production

Both engines can store datetime data, but they do not inherently attach time zone information to those fields—even if `DateTime(timezone=True)` is used in SQLAlchemy.

We want to store and handle all datetimes as UTC internally, while still accommodating differences in how each database engine handles time zone data.

## Original Decision

**We will store all timestamps as UTC (Universal Coordinated Time) throughout the application.**  

This applies to:

- **SQLAlchemy models** (regardless of `timezone=True` usage)
- **Pydantic models**, which validate incoming/outgoing data
- **Service layer** logic for business operations
- **Test code** for local development and CI

## Update (2025-02-15)

After implementation experience, we've refined our approach to simplify datetime handling:

### Key Changes

1. **Remove SQLAlchemy timezone parameters**
   - Remove all `timezone=True` parameters from DateTime columns
   - These parameters provide no actual benefit as the DB engines don't store timezone data
   - Reduces confusion about where timezone enforcement happens

2. **Centralize UTC enforcement in Pydantic**
   - Move ALL timezone validation to Pydantic schemas
   - Create a base validator for consistent enforcement
   - Reject non-UTC datetimes at the schema level
   - No timezone conversion utilities - enforce correct input

3. **Simplify model definitions**

   ```python
   # Before
   created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
   
   # After
   created_at = Column(DateTime(), default=lambda: datetime.now(timezone.utc))
   ```

### Mandated

1. **UTC for storage**: All date/time columns in the database are treated as UTC. Use simple `Column(DateTime())` without timezone parameter.
2. **UTC for Python code**: All new Python datetimes are created with UTC explicitly set, such as `datetime.now(timezone.utc)`.
3. **UTC validation in Pydantic**: Pydantic validators ensure that incoming/outgoing datetimes have a `tzinfo` matching UTC (offset zero).
4. **Front-end** or external clients submit datetimes in UTC format (ISO-8601 with `Z` suffix).

### Implementation Guidelines

#### Base Pydantic Validator

```python
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator  # Updated to V2 style
from typing import Any

class BaseSchemaValidator(BaseModel):
    @field_validator("*", mode="before")  # Updated to V2 style validator
    @classmethod  # Required for V2 field validators
    def validate_datetime_fields(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset().total_seconds() != 0:
                raise ValueError(
                    f"Datetime must be UTC. "
                    f"Got: {value} {'(naive)' if value.tzinfo is None else f'(offset: {value.utcoffset()})'}. "
                    "Please provide datetime with UTC timezone (offset zero)."
                )
        return value

class PaymentCreate(BaseSchemaValidator):
    payment_date: datetime
    # The base validator will handle UTC enforcement
```

Note: As of 2025, we use Pydantic V2 style validators with `@field_validator` instead of the deprecated V1 style `@validator`.

#### SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True)
    payment_date = Column(
        DateTime(),  # No timezone parameter needed
        nullable=False
    )
    created_at = Column(
        DateTime(),
        server_default=func.now(),  # Server's NOW() is fine, treated as UTC
        nullable=False
    )
```

### Prohibited

1. **Naive datetimes** in Python code that lack a `tzinfo` attribute.
2. **timezone=True parameter** in SQLAlchemy DateTime columns.
3. **Timezone conversion utilities** - enforce correct UTC input instead.
4. **Multiple validation layers** - rely on Pydantic schemas only.

## Implementation Strategy

1. **Schema Enhancement**
   - Create BaseSchemaValidator with UTC enforcement
   - Update all Pydantic schemas to inherit from base
   - Add comprehensive schema tests
   - Document validation behavior

2. **Model Simplification**
   - Remove timezone=True from all DateTime columns
   - Update created_at/updated_at defaults
   - Clean up any timezone-specific logic
   - Reinitialize database (development only)

3. **Service Layer Updates**
   - Update datetime creation points
   - Fix date arithmetic for UTC
   - Update tests with UTC fixtures
   - Fix historical analysis

4. **Documentation**
   - Update technical documentation
   - Add schema validation examples
   - Include test cases
   - Document error handling

## Update (2025-03-14)

The implementation of this ADR has been successfully completed:

### Implementation Status

- **✅ All 18 model files** are now fully compliant with the ADR requirements
- All DateTime columns use naive storage without timezone parameters
- All documentation has been updated to clearly indicate UTC approach
- Verification through comprehensive test coverage (100% coverage achieved)

### Key Achievements

- Removed all `timezone=True` parameters from DateTime columns
- Centralized UTC enforcement in Pydantic schemas
- Simplified model definitions for clearer code
- Enhanced docstrings to explicitly reference ADR compliance
- Fixed issues in the accounts model including removing unused imports and improving documentation
- Test suite verifies proper datetime handling across all models

## Update (2025-03-15): Default Factory Datetime Handling

During test implementation, we identified and fixed an important issue with default datetime values:

### Issue Discovered

We found that datetime fields with `default_factory=datetime.now` were creating naive datetimes that bypassed our validation system:

- `default_factory` values are applied after individual field validation
- These naive datetimes weren't being properly converted to UTC
- This created inconsistent timezone behavior for default values vs. explicitly provided values
- Tests could fail with timezone comparison issues across local vs. UTC timezones

### Solution Implemented

We enhanced the `BaseSchemaValidator` with a post-initialization validator:

```python
@model_validator(mode="after")
def ensure_datetime_fields_are_utc(self) -> 'BaseSchemaValidator':
    """Ensures all datetime fields have UTC timezone after model initialization."""
    for field_name, field_value in self.__dict__.items():
        if isinstance(field_value, datetime) and field_value.tzinfo is None:
            # Get the local timezone
            local_tz = datetime.now().astimezone().tzinfo
            
            # First make it timezone-aware as local time
            aware_local_dt = field_value.replace(tzinfo=local_tz)
            
            # Then convert to UTC - this adjusts the actual time value
            utc_dt = aware_local_dt.astimezone(timezone.utc)
            
            # Update the field
            setattr(self, field_name, utc_dt)
    return self
```

### Key Insight

Local timestamps should be *converted* to UTC, not just labeled as UTC:

- Simply adding UTC timezone to naive datetimes (`replace(tzinfo=timezone.utc)`) creates semantically incorrect datetimes
- Proper conversion requires first interpreting the naive datetime in its local context, then converting to UTC
- This ensures the datetime represents the same moment in time, just in different timezone representations

This enhancement ensures full ADR-011 compliance for all datetime fields, including those set by default factories, and fixes a subtle but important timezone handling bug in schema validation.

## Update (2025-03-27): Date Range Handling and Standardized Utilities

We've enhanced our datetime handling approach with standardized utilities and consistent date range handling patterns:

### Date Range Handling

A key decision was made about date range handling:

- **Date ranges are now INCLUSIVE of both start and end dates** to better match business expectations
- Use `start_of_day(start_date)` for the beginning boundary
- Use `end_of_day(end_date)` for the ending boundary
- SQL queries should use `<=` instead of `<` when comparing with end dates

This pattern better represents business understanding of date ranges, where phrases like "from January 1 to January 31" typically include all of January 31.

```python
# Example implementation pattern
range_start = start_of_day(start_date)  # Set time to 00:00:00
range_end = end_of_day(end_date)        # Set time to 23:59:59.999999

# SQL filter pattern 
query = select(Entity).where(
    and_(
        Entity.created_at >= range_start,
        Entity.created_at <= range_end    # Note the <= instead of < for inclusivity
    )
)
```

### New Utility Functions

We've added new standardized helpers to `datetime_utils.py`:

```python
def start_of_day(dt=None):
    """Get start of day (00:00:00) for a given datetime."""
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day)

def end_of_day(dt=None):
    """Get end of day (23:59:59.999999) for a given datetime."""
    dt = dt or utc_now()
    return utc_datetime(dt.year, dt.month, dt.day, 23, 59, 59, 999999)

def date_range(start_date, end_date):
    """Generate a list of dates within a range."""
    current = start_of_day(start_date)
    end = start_of_day(end_date)
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates
```

These functions provide semantic clarity and ensure consistent handling of date boundaries across the application.

## Update (2025-03-28): Repository Standardization and Test Improvements

After reviewing numerous repository implementations, we've identified several patterns and best practices for handling datetime operations:

### Repository Method Patterns

For date range queries, we've standardized on consistent patterns:

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
            Entity.datetime_field <= range_end,
        )
    )
    
    result = await self.session.execute(query)
    return result.scalars().all()
```

### Test Improvements

We've also standardized testing patterns:

1. **Using ADR-011 utilities in tests**:

   ```python
   # Instead of:
   now = datetime.now(timezone.utc)
   start_date = now - timedelta(days=22)
   
   # Use:
   current = utc_now()
   start_date = days_ago(22)
   ```

2. **Safe datetime comparisons**:

   ```python
   # Instead of:
   assert entry.datetime_field >= start_date
   
   # Use database-agnostic comparison:
   assert (entry.datetime_field >= range_start or 
           datetime_equals(entry.datetime_field, range_start))
   ```

3. **Docstring Updates**:

   ```python
   """Test function.
   
   Uses ADR-011 compliant datetime handling with utilities.
   """
   ```

### Validation of Datetime Values

We've also enhanced our approach to validate datetime values from the database:

```python
# In repository methods
for item in db_results:
    # Normalize datetime values from the database
    item.transaction_date = normalize_db_date(item.transaction_date)
```

This ensures consistent date handling regardless of database type, addressing cross-database compatibility issues.

### Cross-Database Date Compatibility

A critical challenge we encountered was handling date values across different database engines. Each engine represents and returns date values differently:

- **SQLite** often returns dates as strings (e.g., "2025-03-27")
- **PostgreSQL/MySQL** return proper datetime or date objects
- **MariaDB** may return custom date types depending on the driver

This inconsistency led to test failures when comparing date values from database results with Python date objects - particularly when running tests with SQLite but deploying with PostgreSQL or MariaDB.

To solve this problem, we've developed a set of database-agnostic date utilities:

```python
def normalize_db_date(date_val):
    """
    Normalize date values returned from the database to Python date objects.
    
    Handles different database engines that may return:
    - String dates (common in SQLite)
    - Datetime objects (common in PostgreSQL)
    - Custom date types
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
    """
    # Normalize target date
    normalized_target = normalize_db_date(target_date)
    
    for d in date_collection:
        if date_equals(normalized_target, d):
            return True
    return False
```

These utilities enable several important capabilities:

1. **Format Normalization**: Automatically detect and convert string dates from SQLite to Python date objects
2. **Type-Safe Comparison**: Compare dates reliably regardless of their original representation
3. **Collection Operations**: Check for date existence in collections with proper normalization
4. **Defensive Programming**: Gracefully handle unexpected formats with fallback mechanisms
5. **Database Portability**: Write code that works identically across all supported database engines

The real-world benefit is significant: repository methods can now handle date values consistently regardless of the database backend, making our codebase truly database-agnostic.

### Implementation Guidelines

1. **For Date Filtering**:
   - Use inclusive date ranges (`<=` for end date) by default
   - Make the inclusivity clear in method documentation
   - Use semantic helper functions (`start_of_day`, `end_of_day`) to clarify intent
   - When querying for records within a date range, normalize date values from query results

2. **For Date Ranges**:
   - Update existing exclusive ranges to use inclusive patterns
   - Document date range behavior in method signatures
   - Use proper timezone-aware comparisons
   - Use the `date_range()` utility to generate complete lists of dates

3. **For Database Compatibility**:
   - Always use database-agnostic utility functions when handling dates from query results
   - Use `normalize_db_date()` before comparing dates from different sources
   - Use `date_equals()` instead of direct `==` for comparing dates from database queries
   - Avoid database-specific date functions (e.g., SQLite's `date()`, PostgreSQL's `DATE_TRUNC`)
   - When working with date collections, use `date_in_collection()` for reliable membership testing
   - Use Python-side date processing rather than database-specific functions when possible

4. **For Repository Methods**:
   - Process dates from query results using our utility functions
   - Add clear docstrings explaining date handling expectations
   - For methods returning date collections, consider pre-normalizing all dates
   - In test code, use normalized comparisons when asserting date equality
   - Log normalized date values in debug statements for easier troubleshooting

5. **For Development/Testing**:
   - Write tests with SQLite that will still pass in production with other database engines
   - Use explicit date assertions that check semantic equality, not just type equality
   - Test date range boundaries thoroughly, especially at month transitions
   - Use utility functions consistently across all repository test files

## Consequences

### Positive

- Simpler, more consistent datetime handling
- Clear separation of concerns (validation in schemas only)
- Reduced confusion about timezone storage
- Better error messages from schema validation
- Simplified model definitions
- Improved testability with naive datetime handling

### Negative

- Strict UTC requirement may require more frontend work
- No automatic timezone conversion (by design)
- Migration needed for existing code

### Mitigation

- Clear error messages help developers provide correct UTC values
- Comprehensive documentation and examples
- Extensive test suite for validation behavior (now at 100% coverage)

## Update (2025-03-29): Enhanced Enforcement and Utility Standardization

Following our recent datetime utility function improvements and standardization efforts, we've further enhanced our datetime handling approach:

### Enhanced Timezone Enforcement

We've implemented stricter enforcement of ADR-011 compliance in datetime functions:

1. **Explicit Rejection of Non-UTC Timezones**
   - Functions now validate that datetimes are either naive or UTC timezone-aware
   - Non-UTC timezone-aware datetimes are rejected with a clear error message:

     ```plaintext
     "Datetime has non-UTC timezone: [datetime]. This violates ADR-011 which requires all 
     datetimes to be either naive (from DB) or timezone-aware with UTC."
     ```

   - No silent timezone conversions - explicit errors instead

2. **Key Functions Updated with Strict Validation**
   - `ensure_utc()`: Now rejects non-UTC timezones instead of converting
   - `datetime_equals()`: Validates timezone compliance before comparison
   - `datetime_greater_than()`: Ensures proper timezone validation
   - Other comparison functions follow the same pattern

### Mandated Use of datetime_utils.py

We are now **explicitly requiring** the use of functions from `datetime_utils.py` throughout the codebase:

1. **Direct Use of Python datetime Functions Prohibited**
   - **NEVER** use `datetime.now()` directly - use `utc_now()` instead
   - **NEVER** create naive datetimes with `datetime(year, month, day)` - use `utc_datetime()` instead
   - **NEVER** use raw timedelta arithmetic - use appropriate utility functions

2. **Essential Functions for Common Tasks**

   | Task | Prohibited | Required |
   |------|------------|----------|
   | Current time | `datetime.now()` | `utc_now()` |
   | Create datetime | `datetime(2025, 3, 15)` | `utc_datetime(2025, 3, 15)` |
   | Days ago | `datetime.now() - timedelta(days=3)` | `days_ago(3)` |
   | Days ahead | `datetime.now() + timedelta(days=3)` | `days_from_now(3)` |
   | Day boundaries | Manual hour/min/sec setting | `start_of_day()`, `end_of_day()` |
   | Date ranges | Manual loop construction | `date_range(start, end)` |
   | Date equality | Direct `==` comparison | `datetime_equals()`, `date_equals()` |
   | Greater/less than | Direct `>`, `<` comparison | `datetime_greater_than()` |

3. **Application Code Requirements**
   - Repository methods must use these functions for all datetime operations
   - Service layer must convert any external datetimes using `ensure_utc()`
   - Database access code must normalize dates with `normalize_db_date()`
   - Test code must create datetimes using these functions

### Safe Datetime Operations

We've enhanced several utilities to handle edge cases more reliably:

1. **Improved `safe_end_date()`**
   - Better handling of month transitions (e.g., January 30 + 3 days)
   - Properly caps at month end when transitioning to shorter months
   - Preserves timezone information from the original datetime
   - Includes additional validation for ADR-011 compliance

2. **Enhanced Comparison Functions**
   - Safer comparison with `ignore_timezone` parameter for comparing DB values
   - New parameter `ignore_microseconds` for precision control in equality checks
   - Explicit rejection of non-compliant datetime values

### Implementation Examples

#### Example 1: Repository Query with Date Range

```python
# Correct implementation
from src.utils.datetime_utils import ensure_utc, start_of_day, end_of_day

def get_transactions_in_range(start_date, end_date):
    """Get transactions within a date range (inclusive)."""
    # Ensure proper timezone handling
    range_start = start_of_day(ensure_utc(start_date))
    range_end = end_of_day(ensure_utc(end_date))
    
    query = select(Transaction).where(
        and_(
            Transaction.date >= range_start,
            Transaction.date <= range_end  # Note inclusive comparison
        )
    )
    return session.execute(query).scalars().all()
```

#### Example 2: Service Function with Date Handling

```python
# Correct implementation
from src.utils.datetime_utils import utc_now, days_from_now, safe_end_date

def schedule_future_payment(amount, days_ahead):
    """Schedule a payment for future date."""
    # Use utility functions rather than raw datetime manipulation
    today = utc_now()
    due_date = safe_end_date(today, days_ahead)
    
    payment = Payment(
        amount=amount,
        date=due_date,
        created_at=today
    )
    return repository.create(payment)
```

#### Example 3: Test Date Assertions

```python
# Correct implementation
from src.utils.datetime_utils import utc_datetime, datetime_equals

def test_payment_date():
    """Test payment date handling."""
    # Create dates with utility functions
    payment_date = utc_datetime(2025, 3, 15)
    payment = create_payment(date=payment_date)
    
    # Use safe comparisons with clear semantics
    assert datetime_equals(payment.date, payment_date)
    # Optionally ignore microseconds if needed
    assert datetime_equals(payment.processed_at, payment.date, 
                         ignore_microseconds=True)
```

### Integration with Existing Guidelines

These new requirements complement our existing guidelines for:

- Date filtering (using inclusive ranges)
- Date range generation
- Database compatibility
- Repository method patterns
- Test improvements

## Update (2025-04-09): Comprehensive Naive Datetime Functions

To further improve our datetime handling, we've expanded our utility functions to include a complete set of naive datetime functions for database operations:

### New Naive Datetime Functions

We've added naive counterparts for all timezone-aware datetime functions to provide a consistent API for both business logic and database operations:

```python
# Naive datetime functions for database storage
naive_days_from_now(days)       # Get naive datetime n days from now
naive_days_ago(days)            # Get naive datetime n days ago
naive_first_day_of_month(dt)    # Get naive first day of month
naive_last_day_of_month(dt)     # Get naive last day of month
naive_start_of_day(dt)          # Get naive start of day (00:00:00)
naive_end_of_day(dt)            # Get naive end of day (23:59:59.999999)
naive_utc_datetime_from_str()   # Parse string to naive datetime
naive_date_range()              # Generate list of naive dates in range
naive_safe_end_date()           # Calculate naive end date with month handling
```

### Benefits of Naive Functions

1. **Direct Database Usage**: These functions produce naive datetimes that can be used directly in database queries without needing to strip timezone information.

2. **Consistent API**: The naming convention and parameter patterns match their timezone-aware counterparts, making it easy to switch between them.

3. **Clear Intent**: Using these functions makes it explicit in the code that the datetime is intended for database storage.

4. **Reduced Errors**: Eliminates common errors from manually converting between timezone-aware and naive datetimes.

### Repository Method Patterns with Naive Functions

We now have two recommended patterns for repository methods:

#### Pattern 1: Using Naive Functions Directly

```python
from src.utils.datetime_utils import naive_start_of_day, naive_end_of_day

def get_by_date_range(start_date, end_date):
    """Get entities within a date range using naive functions."""
    range_start = naive_start_of_day(start_date)
    range_end = naive_end_of_day(end_date)
    
    query = select(Entity).where(
        and_(
            Entity.datetime_field >= range_start,
            Entity.datetime_field <= range_end
        )
    )
    return session.execute(query).scalars().all()
```

#### Pattern 2: Converting Timezone-Aware to Naive

```python
from src.utils.datetime_utils import ensure_utc, start_of_day, end_of_day

def get_by_date_range(start_date, end_date):
    """Get entities within a date range with conversion."""
    # Get timezone-aware datetimes
    aware_start = start_of_day(ensure_utc(start_date))
    aware_end = end_of_day(ensure_utc(end_date))
    
    # Convert to naive for database
    naive_start = aware_start.replace(tzinfo=None)
    naive_end = aware_end.replace(tzinfo=None)
    
    query = select(Entity).where(
        and_(
            Entity.datetime_field >= naive_start,
            Entity.datetime_field <= naive_end
        )
    )
    return session.execute(query).scalars().all()
```

### Implementation Guidelines

1. **For Database Operations**:
   - Use naive datetime functions directly when working with database queries
   - Use clear naming in variables to distinguish between naive and aware datetimes (e.g., `db_date` vs. `aware_date`)
   - Document the use of naive datetimes in function docstrings

2. **For Business Logic**:
   - Continue using timezone-aware functions for all business logic
   - Convert to naive only at the database boundary
   - Use the appropriate naive function rather than manually stripping timezone info

3. **For Testing**:
   - Use naive functions when creating test fixtures for database models
   - Use timezone-aware functions when testing business logic
   - Be explicit about which type of datetime is expected in assertions

## References

- [Python datetime docs](https://docs.python.org/3/library/datetime.html)  
- [SQLAlchemy DateTime docs](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.DateTime)  
- [Pydantic datetime docs](https://docs.pydantic.dev/latest/usage/types/#datetime-types)  
- [MariaDB Timestamp docs](https://mariadb.com/kb/en/datetime/)
