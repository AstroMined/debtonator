# 11. Standardize on Timezone-Aware Datetime Fields

## Status
Proposed

## Context
Recent migration to datetime objects in UTC revealed inconsistencies in our schema definitions. Some schemas use date while others use datetime, leading to timezone-related bugs. This became apparent when working with the historical analysis system, where date comparisons between timezone-aware and naive datetime objects caused errors.

## Decision
Standardize on timezone-aware datetime fields throughout the application to maintain consistency and prevent timezone-related issues. This includes:

1. Using `DateTime(timezone=True)` in SQLAlchemy models
2. Using `datetime` with explicit timezone info in Pydantic schemas
3. Converting any date-only fields to datetime where timezone context is important
4. Maintaining UTC as the standard timezone for stored data
5. Handling timezone conversion in the UI layer

## Consequences

### Positive
- Consistent datetime handling across the application
- Proper timezone support for international users
- Prevention of timezone-related bugs
- More accurate historical analysis
- Better support for time-sensitive operations
- Clearer audit trails with precise timestamps

### Negative
- Need to update multiple schemas and tests
- Temporary increase in complexity during migration
- Need to handle timezone conversion in UI layer
- Slightly increased storage requirements for datetime vs date
- More complex date/time comparisons in queries

### Neutral
- Need to maintain clear documentation about timezone handling
- May need to provide helper functions for common timezone operations
- Will need to update existing tests to use timezone-aware datetime objects

## Implementation Notes

1. Start with core models (Payment, Income, Transaction)
2. Update related schemas (HistoricalPeriodAnalysis, etc.)
3. Add timezone handling utilities if needed
4. Update tests to use timezone-aware datetime objects
5. Document timezone handling expectations in README

## Migration Strategy

1. Identify all date/datetime fields in models and schemas
2. Prioritize fields where timezone information is critical
3. Update models and schemas in small, testable batches
4. Add comprehensive tests for timezone handling
5. Document any breaking changes in CHANGELOG
