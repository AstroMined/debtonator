# Active Context: Debtonator

## Current Focus

Datetime Standardization, Repository Architectural Improvements, Code Cleanup and Quality, Documentation Consolidation

### Recent Changes

1. **Consolidated Decimal Precision Handling ADRs** ✓
   - Combined the original ADR-013 with its update document into a single comprehensive ADR
   - Created a clear narrative showing evolution from ConstrainedDecimal to Annotated types approach
   - Enhanced documentation with detailed technical implementation examples
   - Maintained complete version history from initial proposal through implementation
   - Created archive directory for superseded ADR documents
   - Updated changelog and version information (v0.5.58)

2. **Completed ADR-011 Compliance Test Coverage** ✓
   - Achieved 100% test coverage for schema validation layer
   - Fixed all remaining validator method calls in test files
   - Created targeted tests for model validation edge cases
   - Improved test methods for datetime serialization and validation
   - Fixed validator error assertions to match Pydantic v2 formats
   - Enhanced test coverage for base_schema.py and validation utilities
   - Fixed nested dictionary datetime conversion tests
   - Created comprehensive test suite for model dynamic lookup
   - Improved direct validator method testing patterns
   - Consolidated test code to prevent test sprawl

3. **ADR-011 Compliance Review and Test Improvements** ✓
   - Conducted comprehensive ADR-011 compliance review for schema layer
   - Fixed validator method signatures in test files to match current Pydantic implementation
   - Updated test methods to properly test model validators directly
   - Fixed error assertions to match Pydantic v2 error message formats
   - Improved test coverage for `base_schema.py` and validator methods
   - Fixed test failures for balance history, balance reconciliation, and payments schemas
   - Enhanced test utilities with proper datetime_utils function usage
   - Increased overall schema test coverage to 99%
   - Identified and addressed validator method signature changes for compatibility
   - Implemented consistent validation method calling patterns

4. **Eliminated Circular References in Schema Layer** ✓
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

5. **Test Code Cleanup with Autoflake** ✓
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

6. **Code Organization and Import Pattern Standardization** ✓
   - Standardized import patterns across all layers (models, schemas, repositories)
   - Created dedicated base_schema.py file for schema validation code
   - Removed unnecessary exports from `__init__.py` files
   - Simplified database/base.py to focus on core functionality
   - Eliminated circular import workarounds
   - Used absolute imports consistently for better traceability
   - Improved code organization with clearer module boundaries
   - Reduced technical debt with explicit import patterns
   - Confirmed all tests pass with the new structure

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

4. **Add Naive DateTime Scanner to CI Pipeline**
   - Create GitHub Action for detecting naive datetime usage
   - Integrate scanner with test runs for early detection
   - Add quality gates to prevent introduction of new issues
   - Create documentation for preventing naive datetime usage

## Implementation Lessons

1. **Real Objects Testing Philosophy**
   - Never use mocks in tests - unittest.mock and MagicMock are strictly prohibited:

   ```python
   # Incorrect - using mocks:
   mock_repo = MagicMock()
   mock_repo.get.return_value = None
   service = AccountService(mock_repo)
   
   # Correct - using real objects:
   repo = AccountRepository(db_session)
   service = AccountService(repo)
   ```

   - Always use real repositories with the test database
   - Test database gets set up and torn down between each test
   - Test real cross-layer interactions instead of isolating components
   - Create real test data through schema factories and repository methods
   - Use real schema validation in every test
   - Integration-first approach gives higher confidence in production behavior

2. **Validator Method Calling Patterns**
   - When testing validator methods directly, don't pass the class as first argument:

   ```python
   # Incorrect:
   result = ModelClass.validator_method(ModelClass, value, info)
   
   # Correct:
   result = ModelClass.validator_method(value, info)
   ```

   - Pydantic v2 validator methods are already bound to the class
   - Using datetime_utils functions helps enforce ADR-011 compliance
   - Validation info objects should match Pydantic's ValidationInfo interface
   - Error assertion patterns should match Pydantic v2's error message format

3. **Edge Case Testing for Schema Validators**
   - Test both direct and normal validation paths for model validators
   - Create synthetic objects to test field access patterns
   - Use `object.__setattr__` to bypass initial validation for testing post-validators
   - Check error message formats match Pydantic's actual format
   - Avoid mocking in validator tests and prefer real objects
   - Test fallback paths in model_validate and other methods
   - When testing model lookup functionality, test with both `__model__` references and dynamic name-based lookups

4. **SQL Aggregation Patterns**
   - Use `func.sum(column)` with `group_by()` for proper aggregation
   - For counting with LEFT JOINs, use `func.count(right_table.id)` instead of `func.count()`
   - COUNT(*) counts rows even when joined columns are NULL
   - COUNT(column) only counts non-NULL values of that column
   - This distinction is crucial for accurate counts with OUTER JOINs
   - Always test with empty related tables to verify correct behavior
   - Document SQL aggregation patterns in method docstrings

5. **Nested Object Fields and DateTime Conversion**
   - Top-level datetime fields are properly converted by Pydantic validators
   - Datetime fields in nested containers may require explicit handling
   - Prefer flat object structures when possible for better validation
   - Test both direct field access and nested object access patterns
   - Use composition rather than nesting for complex object structures
   - For nested objects, consider explicit validators for each nesting level
