# Active Context: Debtonator

## Current Focus
Implementing Service Layer Refactoring (ADR-014)

### Recent Changes

1. **Removed Schema Factories Backward Compatibility**
   - Eliminated façade pattern from schema_factories for cleaner imports
   - Updated all factory files to use the decorator pattern consistently
   - Enhanced base utilities with improved typing and constants
   - Fixed CreditLimitHistoryUpdate schema to include required effective_date 
   - Standardized factory return types and docstrings
   - Added comprehensive migration guide in README.md
   - Updated all factories to match current schema requirements
   - Maintained clear "_schema" suffix naming convention for clarity

2. **Implemented Repository Test Pattern Refactoring**
   - Created modular schema factories directory structure to prevent code bloat
   - Added domain-specific factory files organized by entity type
   - Updated ADR014 implementation checklist with detailed testing guidelines
   - Documented the Arrange-Schema-Act-Assert pattern for all repository tests
   - Created base utility functions for schema factory creation
   - Provided clear migration path for existing tests
   - Established BalanceReconciliationRepository as the reference implementation

3. **Fixed Balance Reconciliation Schema Validation** ✓
   - Added adjustment_amount as required field in BalanceReconciliationCreate schema
   - Ensured schema validation correctly enforces NOT NULL constraint from database model
   - Added field validator to verify adjustment_amount equals new_balance - previous_balance
   - Updated BalanceReconciliationUpdate to include new_balance and adjustment_amount fields
   - Documented special handling for repository testing patterns in schema

4. **Fixed Credit Limit History Repository Tests** ✓
   - Updated CreditLimitHistoryUpdate schema to require effective_date field
   - Fixed datetime comparison issue in date range test with timezone-aware handling
   - Aligned schema validation with database NOT NULL constraints
   - Properly handled timezone-aware vs. naive datetime comparison
   - Applied ADR-011 principles for UTC datetime standardization

5. **Improved BaseRepository Update Method** ✓
   - Refactored update method to use proper ORM pattern instead of SQL expressions
   - Enhanced SQLAlchemy session handling for better change tracking 
   - Implemented proper ORM instance retrieval and attribute updates
   - Added explicit session add() to ensure SQLAlchemy tracks changes
   - Fixed issue with onupdate hooks not being triggered

## Next Steps

1. **Fix Schema Factory Tests**
   - Update all existing tests to use direct imports from domain modules
   - Ensure all test cases pass with new factory structure
   - Create robust testing examples using the new factory pattern
   - Add tests for schema validation edge cases

2. **Fix Remaining Test Issues**
   - Address updated_at timestamp issues in ORM updates
   - Fix date_trunc function missing in SQLite for monthly totals tests
   - Complete remaining transaction history repository tests
   - Fix SQLAlchemy ORM identity map issues
   - Enhance testing strategies for timezone handling
   - Resolve additional timezone comparison issues in repository tests

3. **Refactor Remaining Core Services**
   - Apply the repository pattern to BillService and PaymentService
   - Update service tests to use the new pattern
   - Ensure proper validation flow in all services
   - Maintain backward compatibility with existing code

## Implementation Lessons

1. **Technical Debt Avoidance**
   - Backward compatibility layers often become technical debt
   - Clean breaks with clear migration paths are preferable to maintaining compatibility layers
   - Document breaking changes thoroughly to ease transition
   - Prioritize long-term maintainability over short-term convenience

2. **Schema Factory Design Patterns**
   - Use decorators to standardize factory functions
   - Return validated schema instances to catch errors early
   - Provide sensible defaults for common test cases
   - Allow flexibility with kwargs pattern for edge cases
   - Use consistent naming conventions for better code readability

3. **Timezone-Aware vs. Naive Datetimes**
   - Store naive datetimes in the database but enforce UTC semantics
   - Use timezone-aware datetime objects at the schema validation layer
   - When retrieving from DB, add timezone info before passing to schema
   - When comparing datetimes with different timezone info, convert appropriately
   - Always treat database datetime values as semantically UTC

4. **Schema Validation and Database Constraints**
   - Align Pydantic schema requirements with database constraints
   - Required fields in the database should be required in all schemas
   - Field optionality should be consistent between create and update schemas
   - Maintain consistent validation rules across the application
