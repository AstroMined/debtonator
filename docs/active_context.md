# Active Context: Debtonator

## Current Focus
Repository Layer Integration Tests (ADR-014), Ensuring UTC Datetime Compliance (ADR-011), Fixing Circular Dependencies in Schemas, Account Type Expansion Preparation (ADR-016)

### Recent Changes

1. **Fixed Repository Test Datetime Comparison Issues** ✓
   - Fixed comparison issues between timestamps in update operations
   - Added original_updated_at variable to store pre-update timestamp
   - Updated test assertions to compare with stored original timestamp
   - Improved repository test patterns across all model repositories
   - Fixed datetime comparison issues in all "updated_at > test_x.updated_at" assertions
   - Removed debug output from BaseRepository.update()
   - Standardized datetime comparison approach in test files
   - Removed duplicated CRUD tests from repositories/advanced tests

1. **Fixed Payment Source Circular Dependency** ✓
   - Created PaymentSourceCreateNested schema for nested source creation without payment_id
   - Updated PaymentCreate schema to use the new nested schema
   - Fixed validation flow to properly handle the parent-child relationship
   - Enhanced schema factories to support nested source creation
   - Fixed model_dump usage in payment creation
   - Implemented relationship-based ORM approach instead of ID-based references
   - Eliminated circular dependency between Payment and PaymentSource
   - Maintained schema validation while supporting proper parent-child relationships
   - Prevented NULL constraint violations on required fields

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

2. **Improved Historical Data Validation in Liabilities** ✓
   - Removed overzealous validation that prevented past due dates in liability schemas
   - Fixed test failures in integration tests caused by due date validation
   - Added tests to verify past due dates are now accepted (per ADR-002)
   - Enhanced tests to use existing datetime utility functions
   - Refactored test_liabilities_schemas.py to use datetime_utils.py helpers
   - Improved code reuse and maintainability by leveraging established utility functions
   - Fixed potential issues with date comparison and validation
   - Aligned validation with ADR-002 requirements for historical data entry
   - Ensured consistency with other schemas that already allowed past dates

3. **UTC Datetime Compliance Tools Implementation** ✓
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

4. **Schema Reorganization for Better Layering** ✓
   - Separated recurring income schemas from regular income schemas
   - Created dedicated `src/schemas/recurring_income.py` module
   - Migrated all recurring income schemas to the new module
   - Updated API router and service imports to use the new module
   - Created separate unit tests for recurring income schemas
   - Fixed import errors in integration tests and API endpoints
   - Ensured consistent schema layering across the application
   - Maintained feature parity throughout the reorganization

## Next Steps

1. **Complete UTC Datetime Compliance**
   - Fix remaining naive datetime usage in repository tests identified by scanner
   - Add the naive datetime scanner to CI pipeline for continuous monitoring
   - Consider adding utility functions to production code for consistent datetime handling
   - Add automated tests to verify timezone consistency across service boundaries

2. **Service Layer Integration**
   - Refactor remaining services to use repositories
   - Create services for new repository models (PaymentSchedule, DepositSchedule, etc.)
   - Implement proper validation flow in services
   - Update API endpoints to use refactored services
   - Ensure transaction boundaries are respected

3. **Account Type Expansion Implementation (ADR-016)**
   - Implement field naming consistency (`type` → `account_type`) 
   - Fix parameter mapping inconsistencies in schema factories
   - Create consistent schema creation patterns in tests
   - Expand account type options with comprehensive validation
   - Enhance API documentation for account types

## Implementation Lessons

1. **Repository Test Datetime Handling**
   - Store original timestamps before update operations for proper comparison
   - Use explicit variable storage rather than object attribute references
   - Avoid direct comparison of model attributes when dealing with timestamps
   - Be mindful of microsecond precision in datetime objects
   - Remember that SQLAlchemy may generate the same timestamp for very fast operations

2. **UTC Datetime Handling**
   - Always use timezone-aware datetime objects in tests with explicitly set UTC timezone
   - Use helper utilities like `utc_now()` and `utc_datetime()` instead of raw datetime constructors
   - Be careful with naive datetime comparisons in tests that can lead to validation errors
   - SQLite has limitations with timezone handling, so proper application-level enforcement is crucial
   - Standardize on using Python's `datetime.timezone.utc` for consistency
   - Use scanning tools periodically to identify naive datetime usage that might slip through

3. **Repository Test Pattern**
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

4. **SQLAlchemy Query Optimization**
   - Use selectinload for one-to-many relationships
   - Use joinedload for many-to-one relationships
   - Build queries incrementally for better readability
   - Add appropriate ordering for predictable results
   - Use aliased classes for complex joins when needed
   - Optimize relationship loading to prevent N+1 query issues
