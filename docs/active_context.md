# Active Context: Debtonator

## Current Focus
Implementing Service Layer Refactoring (ADR-014)

### Recent Changes

1. **Implemented Repository Test Pattern Refactoring**
   - Created modular schema factories directory structure to prevent code bloat
   - Implemented façade pattern in schema_factories to maintain backward compatibility
   - Added domain-specific factory files organized by entity type
   - Updated ADR014 implementation checklist with detailed testing guidelines
   - Documented the Arrange-Schema-Act-Assert pattern for all repository tests
   - Created base utility functions for schema factory creation
   - Provided clear migration path for existing tests
   - Established BalanceReconciliationRepository as the reference implementation

2. **Enhanced BaseRepository Transaction Handling** ✓
   - Implemented nested transaction support with savepoints
   - Added session.in_transaction() check to detect existing transactions
   - Used session.begin_nested() for active transactions to create savepoints
   - Used session.begin() for standard transactions
   - Fixed transaction tests by properly handling nesting
   - Improved documentation for transaction context manager
   - Added detailed comments explaining the transaction behavior

2. **Fixed Balance Reconciliation Schema Validation** ✓
   - Added adjustment_amount as required field in BalanceReconciliationCreate schema
   - Ensured schema validation correctly enforces NOT NULL constraint from database model
   - Added field validator to verify adjustment_amount equals new_balance - previous_balance
   - Updated BalanceReconciliationUpdate to include new_balance and adjustment_amount fields
   - Documented special handling for repository testing patterns in schema

3. **Fixed Credit Limit History Repository Tests** ✓
   - Updated CreditLimitHistoryUpdate schema to require effective_date field
   - Fixed datetime comparison issue in date range test with timezone-aware handling
   - Aligned schema validation with database NOT NULL constraints
   - Properly handled timezone-aware vs. naive datetime comparison
   - Applied ADR-011 principles for UTC datetime standardization

4. **Fixed Repository Integration Tests** ✓
   - Fixed transaction_history_repository tests with naive vs. UTC datetime handling
   - Added timezone-aware datetime handling for database operations
   - Fixed model updates with proper SQLAlchemy ORM update pattern
   - Ensured proper transaction_date validation in schema updates
   - Resolved transaction_type null constraint issues

5. **Improved BaseRepository Update Method** ✓
   - Refactored update method to use proper ORM pattern instead of SQL expressions
   - Enhanced SQLAlchemy session handling for better change tracking 
   - Implemented proper ORM instance retrieval and attribute updates
   - Added explicit session add() to ensure SQLAlchemy tracks changes
   - Fixed issue with onupdate hooks not being triggered

## Next Steps

1. **Fix Remaining Test Issues**
   - Address updated_at timestamp issues in ORM updates
   - Fix date_trunc function missing in SQLite for monthly totals tests
   - Complete remaining transaction history repository tests
   - Fix SQLAlchemy ORM identity map issues
   - Enhance testing strategies for timezone handling
   - Resolve additional timezone comparison issues in repository tests

2. **Refactor Remaining Core Services**
   - Apply the repository pattern to BillService and PaymentService
   - Update service tests to use the new pattern
   - Ensure proper validation flow in all services
   - Maintain backward compatibility with existing code

3. **Update API Dependency Injection**
   - Update API endpoints to use the refactored services
   - Create dedicated service provider functions
   - Update API tests to use the new dependencies
   - Ensure proper error handling at the API level

## Implementation Lessons

1. **Timezone-Aware vs. Naive Datetimes**
   - Store naive datetimes in the database but enforce UTC semantics
   - Use timezone-aware datetime objects at the schema validation layer
   - When retrieving from DB, add timezone info before passing to schema
   - When comparing datetimes with different timezone info, convert appropriately
   - Always treat database datetime values as semantically UTC

2. **Schema Validation and Database Constraints**
   - Align Pydantic schema requirements with database constraints
   - Required fields in the database should be required in all schemas
   - Field optionality should be consistent between create and update schemas
   - Maintain consistent validation rules across the application

3. **SQLAlchemy ORM Update Patterns**
   - Use ORM instance updates rather than direct SQL update statements
   - Explicitly add changed objects back to the session
   - Ensure flush operations are called to persist changes
   - Let SQLAlchemy handle onupdate hooks rather than manual updates

4. **Database Repository Best Practices**
   - Services should own business logic and validation
   - Repositories focus solely on data access patterns
   - Clear separation improves testability and maintainability
   - Pydantic schemas provide the boundary between layers
