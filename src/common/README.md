# Common Domain Types and Utilities

## Purpose

This module provides shared domain types, utility classes, and constants that are used across different application layers (repositories, services, and API). It ensures consistent type definitions, validation logic, and behavior throughout the application.

## Related Documentation

- [Project Brief](/code/debtonator/docs/project_brief.md)
- [System Patterns](/code/debtonator/docs/system_patterns.md)
- [Tech Context](/code/debtonator/docs/tech_context.md)

## Architecture

The `common` module is a foundational component in our architecture that resolves several key challenges:

1. **Avoiding Circular Dependencies**: By providing a central location for shared types, we prevent circular imports between services and repositories.

2. **Establishing Type Consistency**: Domain types defined here ensure consistent usage across the application.

3. **Proper Architectural Layering**: This module enforces a clear one-way dependency direction:
   - Common domain types have no dependencies on repositories or services
   - Repositories can import from common but not from services
   - Services can import from both repositories and common

### Dependency Direction

```flow
                   ┌────────────┐
                   │    API     │
                   └─────┬──────┘
                         │
                         ▼
                   ┌────────────┐
                   │  Services  │
                   └─────┬──────┘
                         │
                         ▼
                   ┌────────────┐       ┌───────────┐
                   │Repositories│◄──────┤  Common   │
                   └────────────┘       └───────────┘
                         │                    ▲
                         ▼                    │
                   ┌────────────┐             │
                   │ Database   │─────────────┘
                   └────────────┘
```

## Implementation Patterns

### 1. Shared Domain Types

The common module contains shared domain types that are used across multiple layers:

```python
from src.common.cashflow_types import DateType, CashflowWarningThresholds

# In repositories or services
def get_forecast(start_date: DateType, end_date: DateType):
    # Implementation...
    thresholds = CashflowWarningThresholds()
    # ...
```

### 2. Type Re-export Pattern

Services can re-export common types for backward compatibility:

```python
# In src/services/cashflow/cashflow_types.py
from src.common.cashflow_types import CashflowHolidays, CashflowWarningThresholds, DateType

# Add any service-specific extensions here
```

### 3. Layer-Specific Extensions

While common types are shared, each layer may extend them with layer-specific functionality:

```python
# In a service module
from src.common.cashflow_types import CashflowWarningThresholds

class EnhancedWarningThresholds(CashflowWarningThresholds):
    """Service-specific extension with additional thresholds."""
    CRITICAL_BALANCE = Decimal("50.00")
```

## Key Responsibilities

- Provide shared domain types used across application layers
- Define type aliases for consistent parameter typing
- Contain domain constants and threshold values
- House utility classes that implement domain logic without dependencies
- Ensure consistent validation behavior across the application

## Testing Strategy

- Unit test domain types directly with comprehensive coverage
- Test for consistent behavior between layers
- Verify correct implementation of domain rules in shared types
- Ensure backward compatibility for any changes to shared types

## Known Considerations

- Avoid adding dependencies within the common module to prevent new circular imports
- Keep the common module focused on domain types and validation rules
- Don't put business logic that should belong in services in the common types
- Consider versioning for critical domain types if they need to evolve
