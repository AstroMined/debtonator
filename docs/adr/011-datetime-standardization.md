# 11. Standardize on UTC Timezone-Aware Datetime

## Status
Accepted

## Context
The application must handle datetime values consistently to prevent timezone-related bugs and ensure accurate financial calculations. Previous implementation allowed mixing of date and datetime types, leading to inconsistencies and potential errors.

## Decision
We will enforce strict UTC timezone-aware datetime usage throughout the backend:

### Mandated
- All datetime objects MUST be timezone-aware with UTC
- All datetime creation MUST use `datetime.now(ZoneInfo("UTC"))`
- All model fields MUST use `DateTime(timezone=True)`
- All Pydantic schemas MUST use `datetime` (not date)
- All tests MUST create datetime objects with UTC timezone
- All database queries MUST compare timezone-aware datetime objects
- All date arithmetic MUST use datetime objects

### Prohibited
- No timezone-naive datetime objects
- No use of `date` objects
- No timezone conversion utilities
- No mixing of date/datetime types
- No automatic conversion from naive to aware
- No datetime.combine() with naive times
- No storing dates as strings
- No storing timezone-naive datetimes

### Exceptions
Only two places may perform timezone conversions:
1. Bulk Import: When importing external data
2. API Layer: When receiving dates from frontend

## Implementation

### Correct Patterns
```python
# Creating current timestamp
created_at = datetime.now(ZoneInfo("UTC"))

# Creating specific datetime
due_date = datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC"))

# Model definition
class Payment(Base):
    payment_date = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )

# Pydantic schema
class PaymentCreate(BaseModel):
    payment_date: datetime  # Must be UTC aware

    @validator("payment_date")
    def ensure_utc(cls, v):
        if not v.tzinfo or v.tzinfo != ZoneInfo("UTC"):
            raise ValueError("datetime must be UTC timezone-aware")
        return v

# Test fixtures
@pytest.fixture
def test_payment():
    return Payment(
        amount=Decimal("50.00"),
        payment_date=datetime.now(ZoneInfo("UTC"))
    )
```

### Incorrect Patterns
```python
# INCORRECT: Naive datetime
created_at = datetime.now()

# INCORRECT: Date object
due_date = date(2025, 1, 1)

# INCORRECT: Naive datetime in model
payment_date = Column(DateTime())

# INCORRECT: Date field in schema
class PaymentCreate(BaseModel):
    payment_date: date

# INCORRECT: Naive datetime in tests
payment_date = datetime(2025, 1, 1)
```

## Consequences

### Positive
- Consistent datetime handling across the application
- Prevention of timezone-related bugs
- More accurate historical analysis
- Better support for time-sensitive operations
- Clearer audit trails with precise timestamps
- Simplified date arithmetic (no date/datetime conversions)
- Reduced cognitive overhead (only one way to handle dates)

### Negative
- More verbose datetime creation
- Slightly increased storage requirements
- Need to update existing code base

### Mitigation
- Clear documentation and examples
- Comprehensive test coverage
- Static analysis to catch naive datetime usage
- Code review checklist item for datetime handling

## Migration Strategy

### Phase 1: Core Updates
1. Update BaseModel datetime handling
2. Fix all model datetime fields
3. Update all service datetime creation
4. Fix all test datetime objects

### Phase 2: Service Refactor
1. Update cashflow services
2. Update payment services
3. Update income services
4. Update analysis services

### Phase 3: Schema Updates
1. Update all Pydantic schemas
2. Remove any date type usage
3. Update API endpoint documentation

### Phase 4: Test Coverage
1. Update all test fixtures
2. Add datetime validation tests
3. Verify UTC consistency

## References
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)
- [SQLAlchemy DateTime documentation](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.DateTime)
- [Pydantic datetime handling](https://pydantic-docs.helpmanual.io/usage/types/#datetime-types)
