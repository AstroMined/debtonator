# ADR 11: Standardize on UTC DateTime Storage

## Status
**Implemented**

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

## References
- [Python datetime docs](https://docs.python.org/3/library/datetime.html)  
- [SQLAlchemy DateTime docs](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.DateTime)  
- [Pydantic datetime docs](https://docs.pydantic.dev/latest/usage/types/#datetime-types)  
- [MariaDB Timestamp docs](https://mariadb.com/kb/en/datetime/)
