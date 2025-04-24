# Cashflow Repositories

## Purpose

This directory contains repositories for cashflow-related operations, implementing ADR-014 Repository Layer Compliance. These repositories provide a standardized interface for cashflow data access while keeping business logic in the service layer.

## Related Documentation

- [Parent Repository Directory README](/code/debtonator/src/repositories/README.md)
- [ADR-014: Repository Layer Compliance](/code/debtonator/docs/adr/compliance/adr-014-compliance.md)
- [Service Layer Cashflow](/code/debtonator/src/services/cashflow/)

## Architecture

The cashflow repositories are organized into a hierarchy that mirrors the service layer:

```tree
repositories/cashflow/
├── __init__.py
├── base.py                  - Base cashflow repository with shared functionality
├── forecast_repository.py   - Repository for cashflow forecasts
├── metrics_repository.py    - Repository for cashflow metrics
└── transaction_repository.py - Repository for cashflow transactions
```

## Implementation Patterns

### BaseCashflowRepository Pattern

The `BaseCashflowRepository` extends `BaseRepository` and provides:

- Common date handling utilities for cashflow operations
- Warning threshold management
- Timezone handling with ZoneInfo
- Shared functionality for all cashflow repositories

### Repository Specialization Pattern

Each specialized repository focuses on a specific domain:

- **ForecastRepository**: Handles forecast data and trend analysis
- **MetricsRepository**: Manages financial metrics calculations
- **TransactionRepository**: Manages transaction-related operations

### Date Range Handling Pattern

Cashflow repositories use standardized date range handling following ADR-011:

```python
def _prepare_date_range(self, start_date, end_date) -> tuple:
    # For database queries, use naive datetimes
    range_start = naive_start_of_day(start_date)
    range_end = naive_end_of_day(end_date)  # Use end_of_day for inclusive range
    
    return range_start, range_end
```

## Key Responsibilities

- Provide data access for cashflow operations
- Implement ADR-014 compliance for direct database access
- Support service layer with appropriate query methods
- Maintain consistent date range handling
- Enforce proper timezone handling
- Calculate metrics based on database queries
- Facilitate efficient transaction analysis

## Testing Strategy

- Integration tests should use real database fixtures
- Test each repository independently
- Focus on query behavior, not database structure
- Use repository-specific test fixtures
- Test date range handling thoroughly
- Verify timezone handling in queries

## Known Considerations

- Repositories use naive datetimes for database operations
- Services use timezone-aware datetimes for business logic
- Consider performance implications for large dataset queries
- Ensure proper transaction boundaries for write operations
- Consider caching strategies for frequently accessed data
