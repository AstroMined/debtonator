# Active Context: Debtonator

## Current Focus
Repository Test Failure Resolution, Database-Agnostic Repository Implementation, Timezone-aware Datetime Handling, Fixture Corrections, SQLAlchemy Query Patterns

### Recent Changes

1. **Fixed DateTime Handling Issues in Repository Tests (Phase 3)** ✓
   - Fixed all 4 DateTime handling test failures: deposit_schedule, payment_schedule, and payment repositories
   - Implemented safe_end_date utility function to handle month boundary cases
   - Fixed "day is out of range for month" errors with proper date calculations 
   - Used datetime_greater_than and datetime_equals helpers with ignore_timezone=True parameter
   - Fixed timezone comparison issues in payment repository tests
   - Standardized datetime comparison approach across repository tests
   - Created consistent pattern for timezone-aware datetime handling
   - Updated test_failure_resolution_plan.md to track progress (29/52 tests fixed)

2. **Fixed Model Attribute/Relationship Issues (Phase 4)** ✓
   - Fixed all 3 Model Attribute/Relationship test failures in income_category_repository
   - Updated IncomeCategory model to use "incomes" relationship consistently  
   - Fixed attribute name mismatch between test and model (incomes vs income_entries)
   - Updated repository to reference the correct field name (deposited vs is_deposited)
   - Fixed SQLAlchemy case expression syntax in get_categories_with_stats method
   - Added proper SQLAlchemy case import for query expressions
   - Enhanced test fixtures to match model structure
   - Updated test_failure_resolution_plan.md to track progress (32/52 tests fixed)

3. **Fixed Database-Agnostic Aggregation Implementation** ✓
   - Fixed `sqlite3.OperationalError: no such function: date_trunc` error in transaction_history_repository
   - Implemented Python-based aggregation strategy for maximum database compatibility
   - Replaced database-specific SQL functions with application-layer processing
   - Created a reusable pattern for handling database engine differences
   - Successfully passed test_get_monthly_totals test with the new implementation
   - Enhanced data processing with pure Python to ensure cross-database compatibility
   - Used group-by-month logic in memory rather than depending on database functions
   - Updated test_failure_resolution_plan.md to track progress (25/52 tests fixed)

4. **Fixed SQLAlchemy Lazy Loading Issues** ✓
   - Fixed MissingGreenlet errors in CategoryRepository and RecurringBillRepository tests
   - Identified key anti-pattern: using hasattr() in tests which triggers SQLAlchemy lazy loading
   - Created solution pattern: avoiding hasattr() checks on relationships not explicitly loaded
   - Simplified repository implementation to use conditional relationship loading in a single query
   - Eliminated use of multiple separate queries for different relationships
   - Updated test assertions to only check for explicitly loaded relationships
   - Fixed two key tests in Phase 2 database integrity issues
   - Created reusable pattern for fixing similar issues in other repositories

5. **Fixed Repository Test Datetime Comparisons** ✓
   - Fixed "can't compare offset-naive and offset-aware datetimes" errors in multiple repository tests
   - Implemented proper timezone-aware comparisons with datetime_greater_than and datetime_equals helper functions
   - Used ignore_timezone=True parameter for consistent behavior across timezone variants
   - Standardized test assertions to properly check date ranges
   - Updated handling of UTC datetime comparisons in test assertions
   - Fixed statement_history_repository and payment_schedule_repository tests
   - Added proper fixes for timezone handling in repository tests
   - Created patterns for fixing similar timezone issues in other tests

## Next Steps

1. **Continue with Phase 5: Data Count/Value Assertions**
   - Fix Balance History Repository issues (5 failures)
   - Fix Cashflow Forecast Repository issues (4 failures)
   - Fix Bill and Payment Repository issues (3 failures)
   - Fix Statement Repository issues (2 failures)
   - Fix Transaction History Repository issues (5 failures)
   - Use consistent assertion patterns across all repositories

2. **Complete Phase 6: Validation Error Issues**
   - Fix validation error message test in income_category_repository
   - Standardize Pydantic V2 error format handling across tests
   - Create flexible error message testing pattern

3. **Complete UTC Datetime Compliance**
   - Add naive datetime scanner to CI pipeline
   - Consider adding utility functions to production code
   - Review existing test fixtures for timezone consistency

4. **Create ADR Documenting the Test Fixture Architecture**
   - Document the direct SQLAlchemy model instantiation pattern
   - Outline best practices for fixture creation
   - Define responsibility boundaries between fixtures and repositories
   - Create guidance for handling relationships in fixtures

## Implementation Lessons

1. **SQLAlchemy Case Expression Pattern**
   - Use `from sqlalchemy import case` to properly import the case function
   - Use proper syntax for case expressions in SQLAlchemy queries:
   ```python
   func.sum(
       case(
           (Income.deposited == False, 1),
           else_=0
       )
   ).label("pending_count")
   ```
   - Handle boolean expressions in case statements with proper syntax
   - Ensure column labels are properly defined for aggregated results
   - Test complex SQL expressions thoroughly with different inputs

2. **Month Boundary Safe Date Calculation**
   - Use a safe_end_date utility function to handle month boundary issues:
   ```python
   def safe_end_date(today, days):
       """Calculate end date safely handling month transitions."""
       target_date = today + timedelta(days=days)
       year, month = target_date.year, target_date.month
       _, last_day = calendar.monthrange(year, month)
       if target_date.day > last_day:
           return datetime(year, month, last_day, 
                          hour=23, minute=59, second=59, microsecond=999999)
       return datetime(target_date.year, target_date.month, target_date.day,
                     hour=23, minute=59, second=59, microsecond=999999)
   ```
   - Never directly manipulate day component in a datetime object
   - Use calendar.monthrange() to determine the last day of a month
   - Add days using timedelta and then adjust if the result is invalid
   - Handle month transitions properly when calculating end dates

3. **Model Relationship Consistency Pattern**
   - Ensure relationship names are consistent between model definition and usage
   - Update tests to reflect the actual model relationship names
   - Prefer updating tests to match models rather than changing models
   - Use standard SQLAlchemy relationship naming conventions
   - Document relationship names and access patterns in model docstrings
   - Test relationship access explicitly to catch naming inconsistencies
   - When updating model relationships, scan the codebase for all usages

4. **SQLAlchemy Union Query Pattern**
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

5. **Timezone-aware Datetime Comparison Pattern**
   - Use `datetime_greater_than(date1, date2, ignore_timezone=True)` for date comparisons
   - Use `datetime_equals(date1, date2, ignore_timezone=True)` for date equality checks
   - Use helper functions from tests/helpers/datetime_utils.py consistently
   - Apply `days_ago()` and `days_from_now()` for consistent date range creation
   - Use `utc_now()` instead of `datetime.now(timezone.utc)` for standardization
   - Follow the pattern: `assert (datetime_greater_than(date1, date2, ignore_timezone=True) or datetime_equals(date1, date2, ignore_timezone=True))`
   - Be consistent with timezone handling across all repository tests
   - Remember to add proper imports: `from src.utils.datetime_utils import (utc_now, days_from_now, days_ago, datetime_equals, datetime_greater_than)`

6. **Test Fixture Architecture**
   - Create test fixtures using direct SQLAlchemy model instantiation rather than repositories
   - Use db_session directly for model creation, flushing, and refreshing
   - Handle relationships using the flush-then-refresh pattern
   - Ensure field names in fixtures exactly match database model field names
   - Convert aware datetimes to naive with `.replace(tzinfo=None)` for SQLAlchemy storage
   - Implement standard refresh pattern to ensure all relationship data is loaded
   - Create independent fixtures that don't depend on the systems they're testing
