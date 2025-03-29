# Active Context: Debtonator

## Current Focus
Datetime Standardization, Repository Architectural Improvements, Code Cleanup and Quality

### Recent Changes

1. **Eliminated Circular References in Schema Layer** ✓
   - Refactored src/schemas/categories.py to remove circular dependencies
   - Implemented "Reference by ID + Service Composition" approach
   - Removed ForwardRef and model_rebuild() calls for better code maintainability
   - Created new CategoryTree and CategoryWithBillsResponse schemas for rich responses
   - Added service layer composition methods to build rich structures at runtime
   - Updated API endpoints to use new composition approach
   - Updated unit tests and integration tests for new schema classes
   - Updated schema factories to support the new structure
   - Added implementation note to ADR-015 explaining the refactoring
   - Complete redesign eliminates tech debt while maintaining functionality

1. **Test Code Cleanup with Autoflake** ✓
   - Fixed unused variables in test files using autoflake
   - Addressed all identified unused variables in repository test files
   - Carefully reviewed each instance to preserve intentional documentation variables
   - Fixed test_balance_reconciliation_repository_advanced.py unused 'now' variables
   - Fixed test_cashflow_forecast_repository_advanced.py unused 'now' variables 
   - Fixed test_statement_history_repository_advanced.py unused 'now' variable
   - Fixed test_payment_schedule_repository_advanced.py unused 'now' variables
   - Fixed test_deposit_schedule_repository_advanced.py unused 'now' variable
   - Identified unused variables in service files for future refactoring
   - Added code_cleanup.md to document cleanup patterns

1. **Code Organization and Import Pattern Standardization** ✓
   - Standardized import patterns across all layers (models, schemas, repositories)
   - Created dedicated base_schema.py file for schema validation code
   - Removed unnecessary exports from __init__.py files
   - Simplified database/base.py to focus on core functionality
   - Eliminated circular import workarounds
   - Used absolute imports consistently for better traceability
   - Improved code organization with clearer module boundaries
   - Reduced technical debt with explicit import patterns
   - Confirmed all tests pass with the new structure

1. **Enhanced ADR-011 Datetime Standardization** ✓
   - Added explicit mandate to use datetime_utils.py functions throughout the codebase
   - Created comprehensive function table showing prohibited vs. required function usage
   - Implemented strict enforcement of UTC timezone with standardized error messages
   - Updated datetime utility function tests to enforce ADR-011 compliance
   - Fixed tests for ensure_utc(), datetime_equals(), and datetime_greater_than()
   - Added detailed implementation examples for different datetime scenarios
   - Enhanced validation of non-UTC timezone rejection
   - Added comprehensive enforcement guidelines
   - Improved error message standardization for better developer experience

1. **Implemented ADR-017: Payment Source Schema Simplification** ✓
   - Enforced parent-child relationship between Payment and PaymentSource
   - Made PaymentSource creation methods private (_create, _bulk_create_sources)
   - Updated PaymentRepository to enforce at least one source per payment
   - Renamed PaymentSourceCreateNested to PaymentSourceCreate (single schema approach)
   - Removed payment_id requirement from PaymentSourceBase
   - Updated repository integration tests to follow the new pattern
   - Fixed schema factory functions to align with the new design
   - Added future considerations to ADR-017 for completion
   - Improved documentation for parent-child relationship

## Next Steps

1. **Consolidate SQL Aggregation Patterns**
   - Audit repository methods for proper COUNT() handling with JOINs
   - Review SUM() operations for consistency with GROUP BY usage
   - Standardize date range filtering for cross-database compatibility
   - Create pattern library for common repository operations

2. **Enhance Repository Documentation**
   - Document SQL aggregation patterns in repository guides
   - Create examples for proper join handling
   - Update existing method documentation with lessons learned
   - Create guidance for cross-database compatibility

3. **Implement Validation Layer Standardization (ADR-012)**
   - Begin implementation of validation layer aligned with fixed tests
   - Standardize error message handling across validation layers
   - Create consistent pattern for Pydantic validation
   - Ensure compatibility with different Pydantic versions

4. **Create ADR Documenting the Test Fixture Architecture**
   - Document the direct SQLAlchemy model instantiation pattern
   - Outline best practices for fixture creation
   - Define responsibility boundaries between fixtures and repositories
   - Create guidance for handling relationships in fixtures

## Implementation Lessons

1. **SQL Aggregation Patterns**
   - Use `func.sum(column)` with `group_by()` for proper aggregation
   - For counting with LEFT JOINs, use `func.count(right_table.id)` instead of `func.count()`
   - COUNT(*) counts rows even when joined columns are NULL
   - COUNT(column) only counts non-NULL values of that column
   - This distinction is crucial for accurate counts with OUTER JOINs
   - Always test with empty related tables to verify correct behavior
   - Document SQL aggregation patterns in method docstrings

2. **SQLAlchemy Case Expression Pattern**
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

3. **Month Boundary Safe Date Calculation**
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

4. **Module Import and Organization Pattern**
   - Use absolute imports for better traceability and less confusion
   - Keep __init__.py files minimal, ideally just containing docstrings
   - Use dedicated base files (like base_schema.py) instead of putting core functionality in __init__.py
   - Avoid circular imports by proper module organization
   - Extract shared functionality to focused modules
   - Reduce reliance on __all__ exports for better explicitness
   - Follow consistent import patterns across all application layers
