# ADR-029: Transaction Categorization and Reference System

## Status

Proposed

## Executive Summary

This ADR introduces a standardized Transaction Reference System to resolve inconsistencies in how transactions are categorized, referenced, and matched across the application. The decision establishes a robust registry pattern for transaction attributes (source, category, type), replacing hardcoded string matching with standardized lookup methods. This system will ensure consistent transaction handling in forecasting, reporting, and analysis components, reducing errors and improving maintainability across the business logic and repository layers.

## Context

Recent integration tests revealed two significant issues in the cashflow forecasting service:

1. **Inconsistent Transaction Key Generation**: The system uses inconsistent field references for transactions:
   - Income transactions are referenced by type (`income_income`) instead of by source (`income_Salary`)
   - This causes test failures when verifying that specific transactions are included in forecasts
   - The issue extends beyond testing, affecting how users can identify transaction sources in the UI

2. **Fragile Category Matching**: Category filtering is implemented with hardcoded string matching:
   - Transactions are matched using direct string comparison without proper ORM relationship leveraging
   - This approach breaks when categories have similar names or are part of hierarchical relationships
   - The code contains hardcoded assumptions: `("type" in trans and trans["type"] == "bill" and "Utilities" in trans["description"])`

3. **Broader System Impact**:
   - The issues affect multiple components: forecasting, reporting, analytics, and filtering
   - These problems represent a deeper architectural concern about how transactions are classified and referenced
   - The current approach introduces technical debt as new transaction types and categories are added

Addressing these issues is critical as we expand the system's capabilities with additional transaction types, more complex categorization, and advanced filtering.

## Decision

We will implement a Transaction Reference System (TRS) using the registry pattern to standardize how transactions are categorized, referenced, and matched throughout the application. This system will:

1. **Establish a TransactionReferenceRegistry**:
   - Create a central registry in the `src/registry` module alongside other registries
   - Define standard keys for transaction types, sources, and categories
   - Provide consistent methods for generating contribution keys and matching categories
   - Follow the existing registry pattern established in the project

2. **Implement a CategoryMatcher Service**:
   - Create a specialized service for matching transactions to categories
   - Support hierarchical category relationships (parent-child categories)
   - Enable fuzzy matching for similar category names when needed
   - Leverage existing CategoryRepository methods for efficient queries

3. **Standardize Transaction Fields**:
   - Define a consistent approach for referencing transaction attributes
   - Create helper methods for extracting standardized information from different transaction types
   - Support generating consistent keys for contributing factors
   - Eliminate all hardcoded string matching throughout the codebase

We considered alternatives:

1. **Direct Database Queries**: Using direct SQL joins for category matching - rejected due to conflicting with our repository pattern and creating tight coupling between layers.

2. **Simple String Matching Fix**: Just fixing the string matching with more robust conditionals - rejected as it would perpetuate fragile technical debt.

3. **Denormalized Category Tags**: Storing all possible category matches in transaction records - rejected due to data duplication and maintenance overhead.

The registry pattern was selected because:

- It directly aligns with our existing registry pattern (account_type_registry, feature_flag_registry)
- It provides a centralized approach that eliminates string matching technical debt
- It addresses the root cause rather than symptoms of the categorization issues
- It supports advanced features like hierarchical relationships while maintaining code quality

## Technical Details

### Architecture Overview

The Transaction Reference System will follow the registry pattern already established in our codebase through the `src/registry` module. It will consist of:

1. **Core Components**:
   - `TransactionReferenceRegistry`: Central registry managing transaction attribute definitions located in `src/registry/transaction_reference.py`
   - `CategoryMatcher`: Service for matching transactions to categories
   - `TransactionFieldExtractor`: Utility for consistently extracting fields from transactions

2. **Key Interactions**:

   ```mermaid
   graph TD
       A[Services] --> B[TransactionReferenceRegistry]
       A --> C[CategoryMatcher]
       B --> D[Field Definitions]
       B --> E[Key Generators]
       C --> F[Category Relationships]
       C --> G[Match Algorithms]
       C --> H[CategoryRepository]
   ```

3. **Implementation Approach**:
   - Follow the singleton pattern used in other registries
   - Implement a clean, direct solution without temporary workarounds
   - Provide a complete implementation that eliminates string matching
   - Update all affected services to use the registry from the start

### Data Layer

#### Models

No changes to existing models are required. The system will leverage the existing models:

- Category model with its parent-child relationships
- Transaction models with their existing attributes
- Income and Liability models with their specialized fields

#### Repositories

1. **CategoryRepository Enhancements**:
   - Add methods to support hierarchical category queries:

     ```python
     async def get_related_categories(self, category_name: str) -> List[Category]:
         """Get categories related to the given category name including parents and children."""
     
     async def is_category_or_child(self, transaction_category: str, filter_category: str) -> bool:
         """Check if transaction category matches filter category or is a child category."""
     ```

2. **Transaction Repository Integration**:
   - Update repository query methods to support category-based filtering
   - Add methods to efficiently fetch transactions with their complete category information

### Business Logic Layer

#### Schemas

No direct schema changes are required, but we'll add utility methods for validation:

```python
class TransactionSchema(BaseSchemaValidator):
    """Base schema for transaction validation."""
    
    @model_validator(mode="after")
    def validate_category_references(self) -> Self:
        """Validate that category references are valid."""
        # Implementation using CategoryMatcher
```

#### Registry

The TransactionReferenceRegistry will follow the singleton pattern used by other registries:

```python
class TransactionReferenceRegistry:
    """Registry for transaction attribute definitions.
    
    This class implements the singleton pattern to ensure a single registry instance
    exists across the application. Transaction types can be registered with their
    associated fields, categories, and metadata.
    """
    
    _instance: ClassVar[Optional["TransactionReferenceRegistry"]] = None
    
    def __new__(cls) -> "TransactionReferenceRegistry":
        """Create a new TransactionReferenceRegistry instance or return the existing instance."""
        if cls._instance is None:
            cls._instance = super(TransactionReferenceRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the registry with default transaction types."""
        # Transaction type definitions
        self.INCOME = "income"
        self.EXPENSE = "expense"
        self.BILL = "bill"
        self.TRANSFER = "transfer"
        
        # Field access patterns
        self.SOURCE_FIELDS = {
            self.INCOME: "source",
            self.EXPENSE: "description",
            self.BILL: "name",
            self.TRANSFER: "description"
        }
        
        # Category field mappings
        self.CATEGORY_FIELDS = {
            self.INCOME: "category",
            self.EXPENSE: "category",
            self.BILL: "category",
            self.TRANSFER: None  # Transfers typically don't have categories
        }
    
    def get_contribution_key(self, transaction_type: str, identifier: str) -> str:
        """Generate a consistent key for contribution factors."""
        return f"{transaction_type}_{identifier}"
    
    def extract_source(self, transaction: Dict[str, Any]) -> str:
        """Extract the source identifier from a transaction."""
        if "type" not in transaction:
            return "unknown"
            
        field = self.SOURCE_FIELDS.get(transaction["type"], "description")
        return transaction.get(field, "unknown")
    
    def extract_category(self, transaction: Dict[str, Any]) -> Optional[str]:
        """Extract the category from a transaction."""
        if "type" not in transaction:
            return None
            
        field = self.CATEGORY_FIELDS.get(transaction["type"])
        if not field:
            return None
            
        return transaction.get(field)

# Global instance for convenience - follows singleton pattern
transaction_reference_registry = TransactionReferenceRegistry()
```

1. **CategoryMatcher Service**:

   ```python
   class CategoryMatcher(BaseService):
       """Service for matching transactions to categories.
       
       This service provides methods for determining if a transaction belongs
       to a specific category, including handling hierarchical relationships
       between categories.
       """
       
       def __init__(
           self,
           session: AsyncSession,
           feature_flag_service: Optional[FeatureFlagService] = None,
           config_provider: Optional[Any] = None,
       ):
           """Initialize the category matcher service.
           
           Args:
               session: SQLAlchemy async session for database operations
               feature_flag_service: Optional feature flag service for repository proxies
               config_provider: Optional config provider for feature flags
           """
           super().__init__(session, feature_flag_service, config_provider)
           self._registry = transaction_reference_registry
       
       async def matches_category(
           self, 
           transaction: Dict[str, Any], 
           category: Union[str, Category]
       ) -> bool:
           """Check if transaction matches the given category.
           
           This method checks if a transaction belongs to the specified category
           or any of its child categories, supporting hierarchical categorization.
           
           Args:
               transaction: Transaction dictionary
               category: Category name or Category object
               
           Returns:
               True if the transaction matches the category, False otherwise
           """
           # Get transaction category
           transaction_category = self._registry.extract_category(transaction)
           if not transaction_category:
               return False
               
           # Get category repository
           category_repo = await self._get_repository(CategoryRepository)
           
           # Get the category name
           category_name = category.name if isinstance(category, Category) else category
           
           # Check if transaction category matches target category or its children
           return await category_repo.is_category_or_child(
               transaction_category, 
               category_name
           )
   ```

2. **ForecastService Enhancements**:
   Update the ForecastService to use the registry and matcher:

   ```python
   class ForecastService(CashflowBaseService):
       """Service for generating cashflow forecasts."""
       
       def __init__(
           self,
           session: AsyncSession,
           feature_flag_service: Optional[FeatureFlagService] = None,
           config_provider: Optional[Any] = None,
       ):
           """Initialize the forecast service.
           
           Args:
               session: SQLAlchemy async session for database operations
               feature_flag_service: Optional feature flag service for repository proxies
               config_provider: Optional config provider for feature flags
           """
           super().__init__(session, feature_flag_service, config_provider)
           self._transaction_service = TransactionService(
               session, feature_flag_service, config_provider
           )
           self._registry = transaction_reference_registry
       
       async def _calculate_daily_forecast(
           self,
           current_date: DateType,
           accounts: List[Account],
           current_balances: Dict[int, Decimal],
           params: CustomForecastParameters,
       ) -> Optional[CustomForecastResult]:
           """Calculate forecast for a specific day."""
           # ...existing code...
           
           # Get category matcher
           category_matcher = await self._get_service(CategoryMatcher)
           
           # Filter transactions using category matcher
           filtered_transactions = []
           for trans in transactions:
               if params.categories is None:
                   # No filtering
                   filtered_transactions.append(trans)
               else:
                   # Check each requested category
                   for category_name in params.categories:
                       if await category_matcher.matches_category(trans, category_name):
                           filtered_transactions.append(trans)
                           break
           
           # ...existing code...
           
           # Use registry for contribution keys
           for trans in filtered_transactions:
               if trans["amount"] > 0:
                   # Use proper source for income
                   source = self._registry.extract_source(trans)
                   key = self._registry.get_contribution_key(self._registry.INCOME, source)
                   contributing_factors[key] = rounded_amount
               else:
                   # Use proper key for expenses/outflows
                   transaction_type = trans.get("type", self._registry.EXPENSE)
                   description = trans.get("description", "Unknown")
                   key = self._registry.get_contribution_key(transaction_type, description)
                   contributing_factors[key] = rounded_amount
   ```

### API Layer

No immediate changes required for the API layer, but the implementation will support:

1. **Enhanced Filtering**: More robust category filtering for forecast endpoints
2. **Consistent Response Keys**: API responses will use consistent keys for transaction references
3. **Future Expansion**: Groundwork for advanced filtering and categorization features

### Config, Utils, and Cross-Cutting Concerns

1. **Registry Configuration**:
   The registry will be self-contained without external configuration files, following the pattern used by other registries:

   ```python
   # Registration of transaction types happens in _initialize
   def _initialize(self) -> None:
       """Initialize the registry with default transaction types."""
       self._registry_types = {
           "income": {
               "source_field": "source",
               "category_field": "category",
               "description": "Income transaction"
           },
           "expense": {
               "source_field": "description",
               "category_field": "category",
               "description": "Expense transaction"
           },
           "bill": {
               "source_field": "name",
               "category_field": "category",
               "description": "Bill payment"
           },
           "transfer": {
               "source_field": "description",
               "category_field": None,
               "description": "Transfer between accounts"
           }
       }
   ```

2. **Logging Enhancements**:

   ```python
   # Add logging for category matching
   logger.debug(
       "Category matching: transaction=%s, requested_category=%s, result=%s",
       transaction_id, category_name, match_result
   )
   ```

3. **Documentation**:
   We'll add comprehensive documentation in the registry module:

   ```python
   # Add a README.md to the registry module
   """
   # Registry Module

   This module provides central registries for configuration and runtime state
   management across the application. Registries implement the singleton pattern
   for global access with consistent interfaces.
   
   The TransactionReferenceRegistry standardizes how transactions are categorized,
   referenced, and matched throughout the application, eliminating hardcoded string
   matching and providing consistent key generation.
   """
   ```

### Implementation Impact

The changes will affect several components, requiring:

1. **Registry Implementation**:
   - Create TransactionReferenceRegistry in the src/registry module
   - Implement singleton pattern with proper initialization
   - Add comprehensive documentation and tests

2. **Service Implementation**:
   - Create CategoryMatcher service inheriting from BaseService
   - Implement proper category relationship handling
   - Add robust error handling and logging

3. **Service Integration**:
   - Update ForecastService to use the registry and matcher
   - Eliminate all hardcoded string matching
   - Fix key generation for contributing factors
   - Update TransactionService to use standard field extraction

4. **Test Implementation**:
   - Create comprehensive tests for the registry
   - Test hierarchical category matching
   - Verify key generation consistency
   - Test integration with forecast service

## Consequences

### Positive

1. **Improved Robustness**: Eliminates fragile string matching and hardcoded assumptions
2. **Better Maintainability**: Centralizes transaction reference logic in a registry
3. **Extensibility**: Makes adding new transaction types and categories easier
4. **Consistency**: Ensures uniform transaction referencing across the application
5. **Error Reduction**: Reduces bugs related to inconsistent referencing
6. **Enhanced Features**: Supports hierarchical categories and fuzzy matching

### Negative

1. **Implementation Effort**: Requires updating multiple components
2. **Learning Curve**: Introduces new patterns developers must understand
3. **Short-term Complexity**: Adds more abstractions to the codebase
4. **Testing Overhead**: Requires comprehensive testing of the new components

### Neutral

1. **Pattern Alignment**: Follows established registry pattern, similar to account types
2. **Gradual Adoption**: Can be implemented incrementally
3. **Migration Support**: Old code can be maintained during transition

## Quality Considerations

- **Root Cause Focus**: Addresses the root cause of inconsistent transaction referencing
- **Pattern Consistency**: Aligns with established patterns in the codebase
- **Tech Debt Prevention**: Eliminates hardcoded string matching
- **Test Coverage**: Will include comprehensive tests for matchers and extractors
- **Documentation**: Will include detailed documentation in README.md files

## Performance and Resource Considerations

- **Caching Strategy**: The CategoryMatcher will implement caching for relationship information
- **Query Optimization**: Category queries will be optimized for repeated lookups
- **Minimal Impact**: The system adds negligible performance overhead
- **Memory Usage**: Small increase due to registry and caching structures

## Development Considerations

- **Estimated Effort**: Medium (2-3 days for core implementation)
- **Implementation Phases**:
  1. Core Registry and Matcher implementation
  2. ForecastService integration
  3. Gradual adoption in other services
- **Testing Requirements**:
  - Unit tests for registry and matcher
  - Integration tests for forecast services
  - Regression tests for existing functionality

## Timeline

- Implementation Start: 2025-04-28
- Core Components (Registry, Matcher): 2025-04-29
- ForecastService Integration: 2025-04-30
- Testing and Validation: 2025-05-01
- Documentation Updates: 2025-05-02

## Monitoring & Success Metrics

- **Test Pass Rate**: All tests pass with the new system
- **Code Coverage**: >90% coverage for new components
- **Bug Reduction**: Reduction in category-related bugs
- **Code Quality**: Improved maintainability scores

## Team Impact

- **Knowledge Transfer**: Team training on the registry pattern usage
- **Documentation**: Comprehensive documentation in README.md files
- **Code Review Focus**: Special attention to registry pattern implementation

## Related Documents

- ADR-014: Repository Layer Compliance
- ADR-013: Decimal Precision Handling
- System patterns documentation (registry pattern)

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-04-28 | 1.0 | Cline | Initial version |
