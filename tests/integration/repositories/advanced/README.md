# Advanced Repository Tests

## Purpose

This directory contains advanced tests for Debtonator's repository layer. These tests focus on validating complex queries, specialized operations, and relationship handling beyond basic CRUD functions.

## Related Documentation

- [Parent: Repository Tests](/code/debtonator/tests/integration/repositories/README.md)
- [CRUD Tests](/code/debtonator/tests/integration/repositories/crud/README.md)
- [Account Types Advanced Tests](./account_types/banking/README.md)
- [Bill Splits Advanced Tests](./bill_splits/README.md)

## Architecture

Advanced repository tests validate specialized functionality specific to each repository:

- Complex filtering operations
- Relationship-based queries
- Aggregation and calculation methods
- Business logic implemented at the repository level
- Date-range based operations
- Performance optimization methods

These tests build upon the basic CRUD operations tested in the [CRUD tests](/code/debtonator/tests/integration/repositories/crud/README.md) to ensure more complex repository capabilities function correctly.

## Implementation Patterns

### Four-Step Test Pattern

Similar to CRUD tests, advanced tests should follow the four-step pattern:

1. **Arrange**: Set up complex test data and dependencies
2. **Schema**: Create and validate data through schema factories as needed
3. **Act**: Execute the specialized repository method being tested
4. **Assert**: Verify the results with appropriate specificity

### UTC Datetime Compliance Pattern

For tests involving datetime operations, always use the utility functions from `src/utils/datetime_utils.py` to ensure UTC compliance:

```python
from src.utils.datetime_utils import ensure_utc, datetime_equals

# Creating test data with timezone awareness
test_date = ensure_utc(datetime(2025, 4, 1, 12, 0, 0))

# When checking results
assert datetime_equals(result.timestamp, test_date, ignore_timezone=True)
```

This pattern:

- Ensures proper timezone handling
- Makes tests more resilient to environment differences
- Follows ADR-011 datetime standardization

### Comprehensive Test Docstrings

Advanced tests should have detailed docstrings explaining what's being tested and why:

```python
@pytest.mark.asyncio
async def test_get_available_credit_trend(repository, db_session, fixtures):
    """
    Test retrieving available credit trend over time.
    
    This test:
    1. Creates credit account with initial credit limit
    2. Creates several balance history records at different dates
    3. Calls repository method to get available credit trend
    4. Verifies correct calculation of available credit at each point
    """
    # Test implementation
```

## Key Responsibilities

- Test complex query capabilities
- Validate specialized repository methods
- Ensure proper relationship handling
- Test date-range based operations
- Verify proper UTC datetime handling

## Testing Strategy

- Organize tests based on functionality being tested
- Use descriptive test names that explain what's being tested
- Create comprehensive test fixtures for complex scenarios
- Isolate tests to focus on a single behavior at a time
- Test edge cases and boundary conditions
- Pay special attention to timezone handling in date-based tests

## Known Considerations

- Advanced tests may require more complex fixtures than CRUD tests
- Date-based tests should always use `ensure_utc` and proper comparison functions
- When testing decimal calculations, use appropriate tolerance for floating-point arithmetic
- For polymorphic entities, test type-specific behavior in dedicated test files
- Repository methods that affect multiple entities should be tested with appropriate transaction boundaries
- Tests for methods that return collections should verify both content and order when relevant
