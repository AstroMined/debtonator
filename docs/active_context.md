# Active Context: Debtonator

## Current Focus

Account Type Expansion, Service Layer Implementation, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation, Schema Factory Testing, Error Handling System, UTC Datetime Compliance

### Recent Changes

1. **Implemented Comprehensive Naive Datetime Functions (April 9, 2025)** ✓
   - Added naive counterparts for all timezone-aware datetime functions in datetime_utils.py
   - Created naive_days_from_now() and naive_days_ago() functions for database storage
   - Added naive_first_day_of_month() and naive_last_day_of_month() functions
   - Implemented naive_start_of_day() and naive_end_of_day() functions
   - Added naive_utc_datetime_from_str() for string parsing to naive datetimes
   - Created naive_date_range() for generating lists of naive dates
   - Implemented naive_safe_end_date() for month boundary handling
   - Updated documentation in both ADR-011 and UTC datetime compliance guide
   - Added repository method patterns for both naive and timezone-aware approaches
   - Improved database compatibility with direct naive datetime functions

2. **Fixed All Model Fixture Files for UTC Datetime Compliance (April 9, 2025)** ✓
   - Fixed inconsistent datetime handling across all fixture files in tests/fixtures/models
   - Standardized use of naive_utc_now() instead of utc_now().replace(tzinfo=None)
   - Replaced direct use of datetime.now(timezone.utc) with utc_now() from datetime_utils
   - Added proper Args and Returns sections to all fixture docstrings
   - Fixed inconsistent session handling by replacing commit() with flush()
   - Fixed direct model instantiation issues by using proper polymorphic classes
   - Removed debug print statements from fixture code
   - Fixed hardcoded account IDs by using fixture references
   - Fixed inconsistent return type annotations
   - Improved type annotations for parameters
   - All fixture files now follow consistent patterns and best practices

3. **Implemented UTC Datetime Compliance Documentation Synchronization (April 9, 2025)** ✓
   - Added file synchronization notices to all three datetime-related files
   - Created comprehensive code review of fixture files in tests/fixtures/models
   - Updated UTC datetime compliance guide with latest ADR-011 information
   - Added clear guidance on using datetime utility functions
   - Implemented cross-references between documentation and implementation
   - Established datetime_utils.py as the definitive source for function behavior
   - Added repository method patterns for date range handling
   - Included database compatibility guidance for different database engines
   - Added testing best practices for datetime handling
   - Created explicit guidance for maintaining documentation consistency

4. **Fixed Intermittent Test Failures in Income Trends Schema Factory (April 9, 2025)** ✓
   - Identified root cause of random test failures in test_create_income_trends_analysis_schema
   - Added include_seasonality parameter to create_income_trends_analysis_schema factory function
   - Created separate test cases for with and without seasonality scenarios
   - Added test for random behavior to verify ~50% inclusion rate
   - Added test for custom seasonality data
   - Fixed hasattr vs None check issue in original test
   - Implemented deterministic testing approach for better reliability
   - Enhanced test coverage with additional test cases

5. **Implemented Generic Test Infrastructure for BaseRepository (April 7, 2025)** ✓
   - Created test-specific TestItem model for generic repository testing
   - Implemented TestItemCreate/Update/InDB schemas for validation
   - Created schema factory functions for test item creation
   - Added test fixtures for TestItem repository testing
   - Refactored test_base_repository.py to use generic test model
   - Decoupled repository tests from specific business models
   - Fixed import error for AccountCreate schema
   - Added pylint disable=no-member to handle model_dump() warnings
   - All tests passing with proper validation flow

## Next Steps

1. **Complete Error Handling System Implementation**
   - Implement remaining error classes for account types
   - Create consistent error translation between layers
   - Add user-friendly error messages to API responses
   - Implement error handling middleware for API endpoints
   - Add comprehensive documentation for error handling patterns

2. **Complete Schema Factory Test Coverage**
   - Implement remaining tests for account_types schema factories
   - Increase test coverage for specific schema factory components with < 90% coverage
   - Improve test coverage for complex edge cases in nested structures
   - Add cross-factory integration testing for complex relationships
   - Implement tests for additional service-level schema validations

3. **Fix Remaining Schema Factory Implementation Issues**
   - Address validator conflict with discriminator fields in response models
   - Ensure proper handling of field validators in discriminated unions
   - Move complex validation logic to service layer where needed
   - Add robust handling for nested discriminated union validation
   - Document proper schema-service validation patterns

4. **Complete API Layer Integration**
   - Implement GET /banking/overview endpoint
   - Create GET /banking/upcoming-payments endpoint
   - Add POST /accounts/banking endpoint
   - Implement POST /accounts/bnpl/{account_id}/update-status endpoint
   - Create endpoints to retrieve available account types

5. **Update Test Cases for Polymorphic Validation**
   - Extend test coverage for the new Pydantic v2 discriminated union pattern
   - Create comprehensive test cases for all account types
   - Test proper handling of inheritance and discriminator fields

## Implementation Lessons

1. **Naive vs. Timezone-Aware Datetime Functions**
   - Use naive_* functions for database operations (e.g., naive_utc_now(), naive_days_ago())
   - Use timezone-aware functions for business logic (e.g., utc_now(), days_ago())
   - Convert between naive and aware only at the database boundary
   - Use clear variable naming to distinguish between naive and aware datetimes (e.g., db_date vs. aware_date)
   - Document the use of naive datetimes in function docstrings
   - Use naive functions when creating test fixtures for database models
   - Use timezone-aware functions when testing business logic
   - Be explicit about which type of datetime is expected in assertions

2. **Fixture File Standardization**
   - Use naive_utc_now() for all database datetime fields instead of utc_now().replace(tzinfo=None)
   - Always use db_session.flush() instead of db_session.commit() in fixtures
   - Add comprehensive Args and Returns sections to all fixture docstrings
   - Use proper polymorphic classes (e.g., CheckingAccount) instead of base classes with type field
   - Never add helper functions to fixture files; add them to utility modules instead
   - Use fixture references for IDs instead of hardcoding values
   - Remove debug print statements from fixture code
   - Add proper type annotations for all parameters and return values
   - Standardize fixture naming conventions across all files

3. **Schema Factory Test Determinism**
   - Avoid random behavior in tests that can lead to intermittent failures
   - Use explicit parameters to control test behavior (e.g., include_seasonality)
   - Create separate test cases for different scenarios instead of random behavior
   - Implement proper test coverage for both positive and negative cases
   - Use random behavior tests only for verifying distribution, not for functional testing
   - Add clear parameter documentation to make test control obvious

4. **Repository Test Decoupling**
   - Create test-specific models and schemas for testing generic functionality
   - Avoid using business models in tests for generic components
   - Use schema factories to simplify test data creation
   - Follow the Arrange-Schema-Act-Assert pattern consistently
   - Create reusable test fixtures for common test scenarios
   - Implement proper validation flow in all repository tests

5. **Schema Factory Test Edge Cases**
   - Watch for subtle rounding issues in decimal sum assertions (e.g., day_of_month_patterns sum)
   - Verify enum member existence before using in tests to prevent AttributeError
   - Use appropriate assertions for optional fields that may be None but still exist
   - Implement proper tolerance ranges for numerical tests where exact equality isn't required
   - Test both None and explicit values for optional fields
