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
   - Create a central registry for transaction attribute definitions
   - Define standard keys for transaction types, sources, and categories
   - Provide consistent methods for generating contribution keys and matching categories

2. **Implement a CategoryMatcher Service**:
   - Create a specialized service for matching transactions to categories
   - Support hierarchical category relationships (parent-child categories)
   - Enable fuzzy matching for similar category names when needed

3. **Standardize Transaction Fields**:
   - Define a consistent approach for referencing transaction attributes
   - Create helper methods for extracting standardized information from different transaction types
   - Support generating consistent keys for contributing factors

We considered alternatives:

1. **Direct Database Queries**: Using direct SQL joins for category matching - rejected due to conflicting with our repository pattern and creating tight coupling between layers.

2. **Simple String Matching Fix**: Just fixing the string matching with more robust conditionals - rejected as it would perpetuate fragile technical debt.

3. **Denormalized Category Tags**: Storing all possible category matches in transaction records - rejected due to data duplication and maintenance overhead.

The registry pattern was selected because:

- It aligns with our existing architectural patterns (similar to account type registry)
- It provides a centralized approach that improves maintainability
- It allows for extension without code modifications as new types are added
- It supports advanced features like hierarchical relationships and fuzzy matching

## Technical Details

### Architecture Overview

The Transaction Reference System will follow the registry pattern already established in our codebase. It will consist of:

1. **Core Components**:
   - `TransactionReferenceRegistry`: Central registry managing transaction attribute definitions
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
   - Preserve backward compatibility with existing code
   - Enable gradual adoption across the codebase
   - Support both hardcoded and registry-based access during transition

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

#### Services

1. **TransactionReferenceRegistry**:

   ```python
   class TransactionReferenceRegistry:
       """Registry for transaction attribute definitions."""
       
       # Transaction type definitions
       INCOME = "income"
       EXPENSE = "expense"
       TRANSFER = "transfer"
       
       # Field access patterns
       SOURCE_FIELDS = {
           INCOME: "source",
           EXPENSE: "description",
           TRANSFER: "description"
       }
       
       @classmethod
       def get_contribution_key(cls, transaction_type: str, identifier: str) -> str:
           """Generate a consistent key for contribution factors."""
           return f"{transaction_type}_{identifier}"
       
       @classmethod
       def extract_source(cls, transaction: Dict[str, Any]) -> str:
           """Extract the source identifier from a transaction."""
           if "type" not in transaction:
               return "unknown"
               
           field = cls.SOURCE_FIELDS.get(transaction["type"], "description")
           return transaction.get(field, "unknown")
   ```

2. **CategoryMatcher Service**:

   ```python
   class CategoryMatcher(BaseService):
       """Service for matching transactions to categories."""
       
       async def matches_category(
           self, 
           transaction: Dict[str, Any], 
           category: Union[str, Category]
       ) -> bool:
           """Check if transaction matches the given category."""
           # Get transaction category
           transaction_category = self._extract_category(transaction)
           
           # Get category repository
           category_repo = await self._get_repository(CategoryRepository)
           
           # Check if transaction category matches target category or its children
           return await category_repo.is_category_or_child(
               transaction_category, 
               category.name if isinstance(category, Category) else category
           )
       
       def _extract_category(self, transaction: Dict[str, Any]) -> Optional[str]:
           """Extract category from transaction dict."""
           # Implementation with fallbacks for different transaction structures
   ```

3. **ForecastService Enhancements**:
   Update the ForecastService to use the registry and matcher:

   ```python
   class ForecastService(CashflowBaseService):
       """Service for generating cashflow forecasts."""
       
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
                   source = TransactionReferenceRegistry.extract_source(trans)
                   key = TransactionReferenceRegistry.get_contribution_key("income", source)
                   contributing_factors[key] = rounded_amount
               else:
                   # ...existing code...
   ```

### API Layer

No immediate changes required for the API layer, but the implementation will support:

1. **Enhanced Filtering**: More robust category filtering for forecast endpoints
2. **Consistent Response Keys**: API responses will use consistent keys for transaction references
3. **Future Expansion**: Groundwork for advanced filtering and categorization features

### Config, Utils, and Cross-Cutting Concerns

1. **Registry Configuration**:

   ```python
   # Configuration for TransactionReferenceRegistry
   TRANSACTION_TYPE_MAPPINGS = {
       "income": {
           "source_field": "source",
           "default_key": "income",
           "category_field": "category",
           # Add other mappings as needed
       },
       "expense": {
           "source_field": "description",
           "default_key": "expense",
           "category_field": "category",
           # Add other mappings as needed
       },
       # Add other transaction types
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

### Implementation Impact

The changes will affect several components, requiring:

1. **Service Updates**:
   - Modify ForecastService to use the new registry and matcher
   - Update other services that deal with transaction categorization

2. **Test Updates**:
   - Update tests to verify proper transaction references
   - Add tests for category matching edge cases

3. **Migration Strategy**:
   - Implement registry and matcher first
   - Update ForecastService to resolve current test issues
   - Gradually adopt across other services

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
