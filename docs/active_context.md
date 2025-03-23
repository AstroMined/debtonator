# Active Context: Debtonator

## Current Focus
Implementing Default Category Management (ADR-015), Continuing Repository Layer Integration Tests (ADR-014), Ensuring UTC Datetime Compliance (ADR-011), Account Type Expansion Preparation (ADR-016)

### Recent Changes

1. **Account Type Expansion Preparation** ✓
   - Added description field to Account model for better account identification
   - Updated account schemas to include description field
   - Fixed schema factory usage in account repository tests
   - Documented technical debt related to account type handling in ADR-016
   - Identified parameter mapping issues between schema factories and schemas
   - Fixed inconsistent schema creation in tests
   - Prepared groundwork for future account type expansion

1. **Default "Uncategorized" Category Implementation** ✓
   - Created constants for default category configuration in `src/constants.py`
   - Added system flag to categories to prevent modification of system categories
   - Enhanced CategoryRepository with protection for system categories
   - Created default category during database initialization
   - Modified LiabilityCreate schema to use default category when none is specified
   - Added comprehensive test coverage for system category protection
   - Created ADR-015 documenting the Default "Uncategorized" Category implementation
   - Fixed bill split repository integration tests with default category support
   - Implemented repository-level protection for system categories
   - Added schema-level validation for default category

1. **Improved Historical Data Validation in Liabilities** ✓
   - Removed overzealous validation that prevented past due dates in liability schemas
   - Fixed test failures in integration tests caused by due date validation
   - Added tests to verify past due dates are now accepted (per ADR-002)
   - Enhanced tests to use existing datetime utility functions
   - Refactored test_liabilities_schemas.py to use datetime_utils.py helpers
   - Improved code reuse and maintainability by leveraging established utility functions
   - Fixed potential issues with date comparison and validation
   - Aligned validation with ADR-002 requirements for historical data entry
   - Ensured consistency with other schemas that already allowed past dates

2. **UTC Datetime Compliance Tools Implementation** ✓
   - Created comprehensive helper utilities in `tests/helpers/datetime_utils.py` 
   - Implemented scanner script in `tools/scan_naive_datetimes.py` to detect naive datetime usage
   - Added simplified pytest hook in `conftest.py` to warn about naive datetime usage during test runs
   - Created detailed documentation in `docs/guides/utc_datetime_compliance.md`
   - Fixed timezone-related test failures in repository tests
   - Added UTC-aware datetime helper functions (utc_now, utc_datetime, days_from_now, etc.)
   - Created easy-to-use functions for dealing with datetime in tests
   - Implemented post-processing logic to filter out false positives in scanner
   - Improved regex patterns to accurately detect problematic naive datetime usage
   - Fixed most incorrect datetime UTC usage in the repository tests

2. **Schema Reorganization for Better Layering** ✓
   - Separated recurring income schemas from regular income schemas
   - Created dedicated `src/schemas/recurring_income.py` module
   - Migrated all recurring income schemas to the new module
   - Updated API router and service imports to use the new module
   - Created separate unit tests for recurring income schemas
   - Fixed import errors in integration tests and API endpoints
   - Ensured consistent schema layering across the application
   - Maintained feature parity throughout the reorganization

3. **Refactored Additional Model-Specific Repository Tests** ✓
   - Refactored BalanceHistoryRepository tests to implement proper Arrange-Schema-Act-Assert pattern
   - Converted direct dictionary operations to schema-validated workflows
   - Added explicit test fixtures using balance history schema factories
   - Created comprehensive tests for specialized repository methods (get_balance_trend, get_min_max_balance, etc.)
   - Implemented validation error testing to ensure proper schema enforcement
   - Added tests for credit-specific methods like get_available_credit_trend
   - Ensured all test methods explicitly document the four testing phases with clear comments
   - Fixed timezone handling in datetime test assertions for consistency 
   - Improved test organization with logical grouping of related functionality

4. **Repository Integration Test Patterns** ✓
   - Standardized fixture creation with schema validation flow
   - Implemented consistent test-naming patterns across repositories
   - Created separate fixtures for entities with relationships
   - Applied bulk operation testing patterns with validation
   - Standardized method-specific test structures
   - Added relationship loading test patterns
   - Implemented validation error test patterns
   - Ensured proper assertions for operation results
   - Tested transaction boundaries across repositories
   - Added date range and filtering test patterns


## Next Steps

1. **Complete UTC Datetime Compliance**
   - Fix remaining naive datetime usage in repository tests identified by scanner
   - Add the naive datetime scanner to CI pipeline for continuous monitoring
   - Consider adding utility functions to production code for consistent datetime handling
   - Add automated tests to verify timezone consistency across service boundaries

2. **Continue Repository Test Refactoring**
   - Refactor CategoryRepository tests to follow Arrange-Schema-Act-Assert pattern
   - Apply schema validation workflow to BalanceReconciliationRepository tests
   - Update TransactionHistoryRepository tests with proper schema factories
   - Maintain consistency in test structure across all repository tests
   - Verify all specialized methods are properly tested

3. **Service Layer Integration**
   - Refactor remaining services to use repositories
   - Create services for new repository models (PaymentSchedule, DepositSchedule, etc.)
   - Implement proper validation flow in services
   - Update API endpoints to use refactored services
   - Ensure transaction boundaries are respected

## Implementation Lessons

1. **UTC Datetime Handling**
   - Always use timezone-aware datetime objects in tests with explicitly set UTC timezone
   - Use helper utilities like `utc_now()` and `utc_datetime()` instead of raw datetime constructors
   - Be careful with naive datetime comparisons in tests that can lead to validation errors
   - SQLite has limitations with timezone handling, so proper application-level enforcement is crucial
   - Standardize on using Python's `datetime.timezone.utc` for consistency
   - Use scanning tools periodically to identify naive datetime usage that might slip through

2. **Repository Test Pattern**
   - Four-step pattern is essential for proper testing:
     1. Arrange: Set up test dependencies
     2. Schema: Create and validate through Pydantic schemas
     3. Act: Convert validated data to dict and pass to repository
     4. Assert: Verify operation results
   - Create factory functions for all schema types
   - Never create raw dictionaries for repository methods
   - Always validate data through schemas before passing to repositories
   - Include test cases for validation errors
   - Use clear comments to mark each step in test methods for readability

3. **Schema Factory Design**
   - Provide reasonable defaults for all non-required fields
   - Use type hints for parameters and return values
   - Document parameters, defaults, and return types
   - Allow overriding any field with **kwargs
   - Return validated schema instances, not dictionaries
   - Implement factories for all primary and related schemas

4. **SQLAlchemy Query Optimization**
   - Use selectinload for one-to-many relationships
   - Use joinedload for many-to-one relationships
   - Build queries incrementally for better readability
   - Add appropriate ordering for predictable results
   - Use aliased classes for complex joins when needed
   - Optimize relationship loading to prevent N+1 query issues
