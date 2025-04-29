# Registry Module

## Purpose

The registry module provides centralized configuration and runtime state management for the application. It implements the singleton pattern to ensure consistent configuration and behavior across different components, serving as the source of truth for key application metadata.

## Related Documentation

- [Repository Layer README](/code/debtonator/src/repositories/README.md)
- [Service Layer README](/code/debtonator/src/services/README.md)
- [System Patterns: Registry Pattern](/code/debtonator/docs/system_patterns.md)
- [ADR-016: Account Type Expansion](/code/debtonator/docs/adr/backend/016-account-type-expansion.md)
- [ADR-029: Transaction Categorization and Reference System](/code/debtonator/docs/adr/backend/029-transaction-categorization-and-reference-system.md)

## Architecture

The registry module implements a lightweight in-memory state management pattern:

```flow
                  ┌────────────┐
                  │    API     │
                  └─────┬──────┘
                        │
                        ▼
                  ┌────────────┐
                  │  Services  │─────┐
                  └─────┬──────┘     │
                        │            │
                        ▼            ▼
                  ┌────────────┐    ┌───────────┐
                  │Repositories│────►  Registry  │
                  └────────────┘    └───────────┘
                        │                 ▲
                        ▼                 │
                  ┌────────────┐          │
                  │ Database   │──────────┘
                  └────────────┘
```

Key components include:

```tree
src/registry/
├── __init__.py                  # Registry module exports
├── account_types.py             # Registry for account type definitions
├── account_registry_init.py     # Account type registration initialization
├── feature_flags_registry.py    # Registry for feature flag definitions
├── transaction_reference.py     # Registry for transaction field definitions
└── README.md                    # This documentation file
```

## Implementation Patterns

### Singleton Registry Pattern

All registries follow the singleton pattern to ensure a single instance exists across the application:

```python
class SomeRegistry:
    """Registry for some application configuration."""
    
    _instance: ClassVar[Optional["SomeRegistry"]] = None
    
    def __new__(cls) -> "SomeRegistry":
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(SomeRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize registry with default values."""
        # Initialize registry data structures
        self._registry = {}
        
    # Registry-specific methods...

# Global instance for convenience
some_registry = SomeRegistry()
```

### Registration Pattern

Registries provide methods to register and retrieve configuration:

```python
# Registration of types with metadata
account_type_registry.register(
    account_type_id="checking",
    model_class=CheckingAccount,
    schema_class=CheckingAccountSchema,
    name="Checking Account",
    description="Standard checking account for everyday banking",
    category="Banking",
    repository_module="src.repositories.account_types.banking.checking",
    service_module="src.services.account_types.banking.checking",
    feature_flag="BANKING_ACCOUNT_TYPES"
)

# Type-specific retrieval
model_class = account_type_registry.get_model_class("checking")
schema_class = account_type_registry.get_schema_class("checking")

# Filtered retrieval
banking_types = account_type_registry.get_types_by_category("Banking")
```

### Accessor Pattern

Registries provide accessor methods that encapsulate complex lookups:

```python
# Field extraction with fallbacks
source = transaction_reference_registry.extract_source(transaction)
category = transaction_reference_registry.extract_category(transaction)

# Key generation following consistent patterns
key = transaction_reference_registry.get_contribution_key("income", source)
```

### Feature Flag Integration

Registries support feature flag integration for conditional configuration:

```python
# Get account types filtered by enabled features
available_types = account_type_registry.get_all_types(feature_flag_service)

# Check if account type is available with current feature flags
is_valid = account_type_registry.is_valid_account_type(
    "bnpl", 
    feature_flag_service
)
```

## Key Registry Implementations

### AccountTypeRegistry

Manages account type definitions and their associated classes and metadata:

```python
# Stores mapping between account types and their implementations
account_type_registry.register(
    account_type_id="credit",
    model_class=CreditAccount,
    schema_class=CreditAccountSchema,
    name="Credit Card",
    description="Revolving credit account",
    category="Banking"
)

# Provides lookups by type, category, and feature availability
available_types = account_type_registry.get_all_types(feature_flag_service)
banking_types = account_type_registry.get_types_by_category("Banking")
model_class = account_type_registry.get_model_class("credit")
```

### FeatureFlagRegistry

Manages feature flag definitions and their evaluation:

```python
# Registers feature flags with metadata
feature_flag_registry.register(
    flag_name="BANKING_ACCOUNT_TYPES",
    flag_type=FeatureFlagType.BOOLEAN,
    default_value=True,
    description="Enable banking account types",
    metadata={"requires_role": "admin"}
)

# Evaluates flags with context
is_enabled = feature_flag_registry.get_value(
    "BANKING_ACCOUNT_TYPES",
    context={"user_id": "123", "is_admin": True}
)
```

### TransactionReferenceRegistry

Manages transaction field definitions and key generation:

```python
# Defines field access patterns for different transaction types
registry = transaction_reference_registry

# Get proper field name for given transaction type
source_field = registry.SOURCE_FIELDS.get(registry.INCOME)  # "source"
category_field = registry.CATEGORY_FIELDS.get(registry.BILL)  # "category"

# Extract values with proper field access
source = registry.extract_source(transaction)  # Uses correct field
category = registry.extract_category(transaction)  # Uses correct field

# Generate consistent keys for transactions
key = registry.get_contribution_key(registry.INCOME, "Salary")  # "income_Salary"
```

## Key Responsibilities

1. **Type Registration**: Store metadata about system types (account types, transaction types)
2. **Configuration Management**: Store runtime configuration values
3. **Feature Flag Storage**: Store feature flag definitions and values
4. **Field Definition**: Define how to access fields on different entity types
5. **Key Generation**: Generate consistent keys for entity references

## Testing Strategy

1. **Unit Testing**: Registries should have comprehensive unit tests
2. **Initialization Testing**: Ensure registries initialize correctly with default values
3. **Registration Testing**: Test registration and retrieval methods
4. **Edge Cases**: Test with missing values and invalid input
5. **Feature Flag Integration**: Test conditional behavior based on feature flags

## Known Considerations

### Registry Initialization Timing

Registries should be initialized during application startup to ensure all components share the same instance. Each registry follows a specific initialization approach:

1. **AccountTypeRegistry**: Initialized by `account_registry_init.py` during application startup
2. **FeatureFlagRegistry**: Initialized by feature flag system bootstrap code
3. **TransactionReferenceRegistry**: Self-initializes with default types in `_initialize()`

### Global Instance Access

While each registry implements the singleton pattern, a global instance is exported for convenience:

```python
from src.registry.account_types import account_type_registry
from src.registry.feature_flags_registry import feature_flag_registry
from src.registry.transaction_reference import transaction_reference_registry

# Use global instances directly
account_types = account_type_registry.get_all_types()
```

### Thread Safety

All registry implementation provide thread-safe access to their data structures through proper locking mechanisms:

```python
def get_value(self, key):
    """Thread-safe accessor method."""
    with self._lock:
        return self._registry.get(key)
```

### Registry vs Configuration

Registries differ from configuration in key ways:

1. **Registries**: Used for type metadata, field definitions, and runtime state
2. **Configuration**: Used for application settings and environment-specific values

Use registries when you need to:

- Store metadata about system types
- Define field access patterns
- Manage runtime state
- Control feature availability

Use configuration when you need to:

- Store environment-specific settings
- Configure external service connections
- Set operational parameters

## Usage Guidelines

### Registry Implementation Guidelines

When implementing a new registry:

1. Follow the singleton pattern with `_instance` class variable
2. Implement `__new__` method to return existing instance
3. Implement `_initialize` method for initial state setup
4. Create a global instance at the module level
5. Add comprehensive docstrings and type hints
6. Include thread safety if the registry will be accessed from multiple threads

### Registry Usage Guidelines

When using registries:

1. Import the global instance, not the class
2. Use accessor methods rather than direct attribute access
3. Pass feature_flag_service to filtering methods when available
4. Handle missing values gracefully
5. Use proper error handling for registry operations
