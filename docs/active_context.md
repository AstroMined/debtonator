# Active Context: Debtonator

## Current Focus
Repository Test Failure Resolution, Timezone-aware Datetime Handling, Fixture Corrections, SQLAlchemy Query Patterns

### Recent Changes

1. **Fixed SQLAlchemy Lazy Loading Issues** ✓
   - Fixed MissingGreenlet errors in CategoryRepository and RecurringBillRepository tests
   - Identified key anti-pattern: using hasattr() in tests which triggers SQLAlchemy lazy loading
   - Created solution pattern: avoiding hasattr() checks on relationships not explicitly loaded
   - Simplified repository implementation to use conditional relationship loading in a single query
   - Eliminated use of multiple separate queries for different relationships
   - Updated test assertions to only check for explicitly loaded relationships
   - Fixed two key tests in Phase 2 database integrity issues
   - Created reusable pattern for fixing similar issues in other repositories

2. **Fixed Repository Test Datetime Comparisons** ✓
   - Fixed "can't compare offset-naive and offset-aware datetimes" errors in multiple repository tests
   - Implemented proper timezone-aware comparisons with datetime_greater_than and datetime_equals helper functions
   - Used ignore_timezone=True parameter for consistent behavior across timezone variants
   - Standardized test assertions to properly check date ranges
   - Updated handling of UTC datetime comparisons in test assertions
   - Fixed statement_history_repository and payment_schedule_repository tests
   - Added proper fixes for timezone handling in repository tests
   - Created patterns for fixing similar timezone issues in other tests

2. **Identified and Fixed Fixture Mismatch Pattern** ✓
   - Discovered common issue with tests using incorrect fixture types
   - Fixed payment_schedule_repository_advanced test with proper fixture references
   - Changed test_multiple_schedules to test_multiple_payment_schedules for proper typing
   - Standardized fixture naming for better consistency
   - Documented pattern to help resolve similar fixture mismatch issues
   - Created comprehensive plan for remaining fixture mismatches
   - Enhanced test infrastructure with better fixture management
   - Improved test reliability by using proper type-specific fixtures

3. **Fixed Test Date Range Handling** ✓
   - Enhanced test_get_by_date_range assertions to properly check date ranges
   - Updated test_find_overdue_schedules to use proper datetime comparisons
   - Used helper functions days_ago and days_from_now consistently
   - Fixed date range boundary testing with proper timezone awareness
   - Enhanced test_get_auto_process_schedules with proper date range handling
   - Standardized date range comparison pattern across all repository tests
   - Improved test readability with helper functions for date operations
   - Enhanced test reliability with consistent date handling

4. **Refactored Test Fixtures to Use Direct SQLAlchemy Model Instantiation** ✓
   - Replaced repository-based fixture data creation with direct SQLAlchemy model instantiation
   - Fixed circular dependency issues where repository tests were using fixtures that themselves used repositories
   - Updated fixtures in income, payments, recurring, schedules, statements, and transactions fixture files
   - Removed repository dependencies from fixtures completely
   - Used db_session directly in fixtures for model instantiation
   - Properly handled relationships with the flush-then-refresh pattern
   - Ensured test fixtures use the correct field names matching actual model fields
   - Applied consistent pattern for timezone handling with naive datetimes for DB storage

5. **Fixed SQLAlchemy Union Query ORM Mapping Loss** ✓
   - Fixed 'int' object has no attribute 'primary_account_id' error in LiabilityRepository
   - Discovered SQL UNION operations could cause ORM mapping loss in SQLAlchemy
   - Implemented sustainable two-step query pattern to preserve entity mapping
   - First: Collect IDs from separate queries for primary accounts and bill splits
   - Second: Make a final query using ID list to retrieve full entity objects
   - Used Liability.id.in_(combined_ids) pattern instead of direct UNION
   - Documented pattern as a best practice for handling complex query combinations
   - Added additional defensive handling for empty result sets

6. **Enhanced Test Failure Resolution Documentation** ✓
   - Updated test_failure_resolution_plan.md with new progress tracking (17/52 tests fixed)
   - Added fixture mismatch pattern documentation to help resolve similar issues
   - Documented timezone comparison patterns for repository tests
   - Created comprehensive tracking for remaining test failures by category
   - Improved implementation guidelines with detailed patterns for fixing similar issues
   - Added examples for proper timezone-aware comparison
   - Organized test failures by type for more systematic resolution
   - Created clear priorities for remaining test failures
   - Added new "SQLAlchemy Union ORM Mapping Pattern" section

## Next Steps

1. **Apply Union Query Pattern to Similar Repository Methods**
   - Check payment_repository methods for similar UNION issues
   - Apply two-step query pattern to recurring_bill_repository where needed
   - Fix any other repositories that might have ORM mapping loss with UNION queries
   - Ensure all repository return types match actual returned data types
   - Add defensive handling for empty result sets consistently
   - Check for similar pattern application in transaction_history_repository

2. **Continue Phase 1: Complete DateTime Standardization**
   - Fix remaining test_get_upcoming_schedules issues in deposit_schedule_repository and payment_schedule_repository
   - Fix "day is out of range for month" errors with proper date calculations
   - Apply datetime_greater_than and datetime_equals helpers to remaining tests

2. **Continue Phase 2: Database Integrity Issues**
   - Fix NOT NULL constraint failures in category_repository_advanced tests
   - Fix relationship loading issues in liability_repository_advanced
   - Fix assertion issues in recurring_bill_repository_advanced
   - Fix category-income relationships in income_category_repository_advanced

3. **Continue Phase 4a: Fixture Mismatch Issues**
   - Fix deposit_schedule_repository_advanced tests using improper fixtures
   - Systematically fix all tests using test_multiple_schedules instead of correct type-specific fixtures
   - Apply fixture naming consistency pattern across all repository tests
   - Ensure proper fixture relationships for all test cases

4. **Create ADR Documenting the Test Fixture Architecture**
   - Document the direct SQLAlchemy model instantiation pattern
   - Outline best practices for fixture creation
   - Define responsibility boundaries between fixtures and repositories
   - Create guidance for handling relationships in fixtures

## Implementation Lessons

1. **SQLAlchemy Union Query Pattern**
   - Avoid direct UNION operations with complex ORM mappings
   - Use a two-step query approach for complex multi-source queries:
     1. Collect IDs from separate queries
     2. Use a final query with `entity.id.in_(combined_ids)` to maintain ORM mapping
   - Process result sets separately before combining to prevent ORM mapping loss
   - Add defensive empty list checks to handle edge cases gracefully
   - Always test that returned objects have expected attributes and methods
   - Use `.all()` before performing Python-side operations on database results
   - Remember to handle duplicates with set operations when appropriate
   - Clear queries return complete entity objects, not just scalar values

2. **Timezone-aware Datetime Comparison Pattern**
   - Use `datetime_greater_than(date1, date2, ignore_timezone=True)` for date comparisons
   - Use `datetime_equals(date1, date2, ignore_timezone=True)` for date equality checks
   - Use helper functions from tests/helpers/datetime_utils.py consistently
   - Apply `days_ago()` and `days_from_now()` for consistent date range creation
   - Use `utc_now()` instead of `datetime.now(timezone.utc)` for standardization
   - Follow the pattern: `assert (datetime_greater_than(date1, date2, ignore_timezone=True) or datetime_equals(date1, date2, ignore_timezone=True))`
   - Be consistent with timezone handling across all repository tests
   - Remember to add proper imports: `from src.utils.datetime_utils import (utc_now, days_from_now, days_ago, datetime_equals, datetime_greater_than)`

2. **Fixture Mismatch Resolution Pattern**
   - Look for fixture parameter names like `test_multiple_schedules` in test function parameters
   - Replace with proper type-specific fixtures like `test_multiple_payment_schedules`
   - Verify fixture type matches the repository being tested
   - Follow naming convention: `test_multiple_[model_name_plural]`
   - Check fixture imports in conftest.py to ensure proper type availability
   - For deposit schedules, use `test_multiple_deposit_schedules` instead of `test_multiple_schedules`
   - For payment schedules, use `test_multiple_payment_schedules` instead of `test_multiple_schedules`
   - Apply the pattern systematically to all tests in the file

3. **Test Fixture Architecture**
   - Create test fixtures using direct SQLAlchemy model instantiation rather than repositories
   - Use db_session directly for model creation, flushing, and refreshing
   - Handle relationships using the flush-then-refresh pattern
   - Ensure field names in fixtures exactly match database model field names
   - Convert aware datetimes to naive with `.replace(tzinfo=None)` for SQLAlchemy storage
   - Implement standard refresh pattern to ensure all relationship data is loaded
   - Create independent fixtures that don't depend on the systems they're testing
