# Active Context: Debtonator

## Current Focus

Account Type Expansion, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation, Schema Factory Testing, Error Handling System, UTC Datetime Compliance, Utils Module Test Coverage, Repository Test Pattern Implementation, API Layer Implementation, Test Infrastructure Improvement

### Recent Changes

1. **Refactored Feature Flag Registry Tests (April 13, 2025)** ✓
   - Converted class-based tests to function-based approach:
     - Transformed TestFeatureFlagRegistry class into standalone test functions
     - Maintained same test logic and assertions to ensure equivalent coverage
     - Organized tests into logical groups with clear section comments
     - Added proper docstrings to improve test readability
   - Enhanced test fixtures for better isolation:
     - Added registry_with_predefined_flags fixture to tests/fixtures/fixture_feature_flags.py
     - Created standardized test setup with boolean, percentage, user segment, and time-based flags
     - Improved fixture reusability across multiple test functions
     - Fixed fixture scope for better test isolation
   - Fixed datetime format handling in time-based feature flag tests:
     - Resolved ValueError issues with datetime string parsing
     - Improved time-based flag test reliability
     - Fixed test failures related to microsecond precision in datetime strings
     - Ensured consistent datetime handling across all tests
   - These improvements ensure:
     - Better alignment with project's function-based testing standards
     - Improved test organization and maintainability
     - More reliable time-based feature flag testing
     - Consistent fixture usage across feature flag tests

2. **Improved Feature Flag Schema Test Coverage (April 13, 2025)** ✓
   - Reorganized feature flag tests into a more logical structure:
     - Created dedicated feature_flags/ package with specialized test modules
     - Separated tests by functionality: base, flag types, operations, requirements, history/metrics, context
     - Improved test organization for better maintainability and understanding
   - Enhanced FeatureFlagContext schema validation:
     - Added boolean field validation for is_admin and is_beta_tester
     - Added IP address format validation for client_ip
     - Implemented proper validators with clear error messages
   - Fixed test failures in feature flag toggle validation:
     - Updated regex patterns to match actual Pydantic v2 error messages
     - Added comprehensive tests for various input types
     - Ensured proper validation of boolean values and IP addresses
   - Improved overall test coverage:
     - Increased feature_flags.py coverage from 90% to 97%
     - Added targeted tests for edge cases and validation rules
     - Reduced uncovered code to minimal defensive code sections

2. **Fixed Schema Validation in Payment App Account Type (April 12, 2025)** ✓
   - Resolved validation issues in payment app schema:
     - Modified field validators to only check the format of card_last_four, removing cross-field validation
     - Added model validators to handle the relationship between has_debit_card and card_last_four
     - Updated test to explicitly set has_debit_card=True when providing card_last_four
     - Fixed implicit debit card handling in model validators
   - Implemented model validator improvements:
     - Added automatic has_debit_card=True setting when card_last_four is provided
     - Fixed validation flow to handle fields not explicitly set
     - Improved error messages for validation failures
     - Added proper docstrings explaining validation behavior
   - Enhanced test coverage for edge cases:
     - Updated test_card_last_four_validation_edge_cases to use explicit has_debit_card=True
     - Fixed test expectations to match actual validation behavior
     - Maintained backward compatibility with existing code
     - Ensured all tests pass with the new validation approach
   - These fixes ensure:
     - Proper validation flow between field and model validators
     - Consistent behavior for card_last_four and has_debit_card fields
     - Clear error messages for validation failures
     - Improved test coverage for edge cases

2. **Fixed Repository CRUD Integration Test Issues (April 12, 2025)** ✓
   - Resolved multiple test failures in repository integration tests:
     - Fixed category repository tests with proper system category initialization
     - Added required `income_id` field to deposit schedule schema for database consistency
     - Enhanced BaseRepository with robust field filtering for model compatibility
     - Updated schema factory to align with model requirements
     - Fixed schema-model mismatches to prevent database constraint violations
   - Implemented schema-model alignment improvements:
     - Added comprehensive field discovery in BaseRepository.create()
     - Ensured foreign key fields are properly identified and preserved
     - Added relationship field filtering for database operations
     - Created better error propagation for invalid fields
     - Improved schema-to-model transformation for repository operations
   - Enhanced test coverage for schema-model interactions:
     - Added test cases for field filtering behavior
     - Updated schema factory tests to verify correct default value behavior
     - Added schema-model transformation tests
     - Fixed assertions to match expected filtering behavior
     - Added detailed comments about filtering behavior in tests
   - These fixes ensure:
     - System categories (ID=1) are properly protected from modification/deletion
     - Repository operations correctly handle required fields in database models
     - Schemas can include API-specific fields that don't exist in database models
     - Test cases properly verify the field filtering and validation behavior
     - The codebase consistently handles schema-model field mappings

3. **Created and Implemented PolymorphicBaseRepository Class (April 12, 2025)** ✓
   - Designed and implemented a specialized base repository for polymorphic entities:
     - Created `PolymorphicBaseRepository` class that extends `BaseRepository`
     - Disabled base `create` and `update` methods with `NotImplementedError`
     - Implemented `create_typed_entity` and `update_typed_entity` methods
     - Added automatic field validation and filtering based on model class
     - Integrated with type registries for proper model class lookup
   - Addressed critical technical debt in polymorphic entity handling:
     - Eliminated SQLAlchemy warnings about "Flushing object with incompatible polymorphic identity"
     - Provided clear separation between repositories for simple and polymorphic entities
     - Created consistent interface for all polymorphic repositories
     - Ensured proper type handling and identity management
     - Prevented setting invalid fields that don't exist on specific model classes
   - Updated documentation and implementation plans:
     - Added pattern to system_patterns.md with detailed explanation and examples
     - Updated ADR-016 with the new polymorphic repository pattern
     - Updated implementation checklist with new tasks
     - Prioritized implementation in next steps
   - Future-proofed design for upcoming entity types:
     - Pattern will support statement types described in ADR-025
     - Scales to support any number of polymorphic entity types
     - Simplifies adding new polymorphic entity types
     - Provides consistent interface across all polymorphic repositories
   - Implementation includes:
     - Proper registry integration with account_type_registry
     - Field filtering to prevent invalid fields
     - Type verification during updates
     - Detailed error messages for troubleshooting
     - Comprehensive documentation with example usage

4. **Standardized Banking Account Type Repository Tests (April 12, 2025)** ✓
   - Identified inconsistencies in repository test patterns across banking account types:
     - Found that ewa, bnpl, and payment_app tests followed proper CRUD pattern
     - Discovered checking, credit, and savings tests mixed CRUD and advanced operations
     - Identified repository fixture usage issues in checking, credit, and savings repositories
   - Fixed repository fixture usage in checking, credit, and savings repositories:
     - Updated to use repository_factory as a function rather than trying to call a method on it
     - Aligned with the pattern used in the working ewa, bnpl, and payment_app repositories
     - Fixed `AttributeError: 'function' object has no attribute 'create_account_repository'` errors
   - Standardized CRUD test files to include only basic CRUD operations:
     - Implemented consistent test_create_*_account, test_get_*_account, test_update_*_account, test_delete_*_account pattern
     - Ensured consistent naming across all banking account types
     - Applied the four-step pattern (Arrange-Schema-Act-Assert) consistently
   - Moved advanced repository tests to the appropriate advanced test files:
     - Relocated polymorphic identity tests (get_with_type, get_by_type)
     - Moved specialized create/update tests (create_typed_account, update_typed_entity)
     - Maintained all existing test functionality when moving tests
   - Updated method calls across all test files:
     - Changed create_typed_account to create_typed_entity
     - Changed update_typed_account to update_typed_entity
     - Updated method parameter order to match new interface
     - Standardized parameter naming across all files

5. **Consolidated Feature Flag Test Fixtures (April 12, 2025)** ✓
   - Identified and resolved issues with scattered feature flag fixtures:
     - Found 7 overlapping fixture files with duplicate functionality
     - Identified transaction rollback issues causing cascading test failures
     - Resolved unique constraint violations in database operations
     - Fixed async/sync handling inconsistencies in fixture functions
   - Created a consolidated feature flag fixture system:
     - Created a single canonical fixture file at tests/fixtures/fixture_feature_flags.py
     - Implemented proper async fixtures with pytest_asyncio.fixture decorators
     - Added timestamp-based unique identifiers to prevent name collisions
     - Fixed transaction management for more reliable tests
   - Updated test file to use the new consolidated fixtures:
     - Modified test_feature_flag_service.py to use the new fixture pattern
     - Simplified test approach with direct database model creation
     - Implemented proper service reinitialization between tests
     - Ensured tests are properly isolated from each other
   - Related improvements:
     - Updated conftest.py to reference the new consolidated fixture file
     - Removed obsolete fixture files to prevent confusion
     - Verified tests pass with the new consolidated approach

## Next Steps

1. **Complete Method Name Transition**
   - Verify no remaining references to create_typed_account and update_typed_account
   - Update any documentation outside of test and implementation files
   - Ensure API documentation reflects new method names
   - Add comprehensive docstrings for the new methods
   - Add examples of using the new methods to system_patterns.md

2. **Create Unit Tests for PolymorphicBaseRepository**
   - Implement test_polymorphic_base_repository.py to verify core functionality
   - Test disabled base methods raise proper exceptions
   - Test proper field filtering and validation
   - Create test scenarios for error handling cases
   - Verify proper registry integration
   - Create tests for update handling with type validation

3. **Complete Error Handling System Implementation**
   - Implement remaining error classes for account types
   - Create consistent error translation between layers
   - Add user-friendly error messages to API responses
   - Implement error handling middleware for API endpoints
   - Add comprehensive documentation for error handling patterns

4. **Continue Repository Test Refactoring**
   - Refactor account type advanced tests:
     - advanced/account_types/banking/test_bnpl_advanced.py
     - advanced/account_types/banking/test_ewa_advanced.py
     - advanced/account_types/banking/test_payment_app_advanced.py
   - Refactor other repository tests:
     - test_base_repository.py
     - test_factory.py
     - test_feature_flag_repository.py
     - account_types/banking/test_checking.py
     - account_types/banking/test_credit.py
     - account_types/banking/test_savings.py
     - bill_splits/test_bill_splits_with_account_types.py

5. **Complete Schema Factory Test Coverage**
   - Implement remaining tests for account_types schema factories
   - Increase test coverage for specific schema factory components with < 90% coverage
   - Improve test coverage for complex edge cases in nested structures
   - Add cross-factory integration testing for complex relationships
   - Implement tests for additional service-level schema validations

## Implementation Lessons

1. **Polymorphic Repository Pattern**
   - Use specialized base repository for polymorphic entities (`PolymorphicBaseRepository`)
   - Disable base `create` and `update` methods with `NotImplementedError` to prevent incorrect usage
   - Implement type-specific creation and update methods (`create_typed_entity`, `update_typed_entity`)
   - Always use concrete subclasses that match the intended polymorphic type
   - Integrate with type registries for proper model class lookup
   - Implement automatic field validation and filtering based on model class
   - Ensure proper type handling and identity management
   - Prevent setting invalid fields that don't exist on specific model classes
   - Use consistent interface for all polymorphic repositories
   - Design for future expansion to support any number of polymorphic entity types

2. **Repository Fixture Usage Patterns**
   - Use repository_factory as a function, not as an object with methods
   - Understand the difference between class-based and function-based fixtures
   - Ensure consistent fixture usage patterns across similar repository types
   - Verify fixture implementation matches usage in tests
   - Document fixture usage patterns for team reference

3. **Repository Test Organization**
   - Separate CRUD tests from advanced repository tests
   - Place basic CRUD operations (create, get, update, delete) in crud/ directory
   - Place specialized operations in advanced/ directory
   - Maintain consistent test naming across similar repository types
   - Follow established patterns from working test files

4. **Feature Flag System Architecture**
   - Centralize feature flag enforcement at architectural boundaries instead of scattering checks
   - Use proxy/interceptor patterns to separate business logic from feature gating
   - Implement domain-specific exceptions for better error handling and clarity
   - Store both flag values AND requirements in the database for runtime configuration
   - Use caching with appropriate TTL for performance optimization
   - Implement account type extraction to support feature flags for specific account types
   - Follow bottom-up implementation approach starting at repository layer
   - Ensure consistent async/await patterns throughout the system
   - Use cache-aware testing strategies to handle TTL caching effects
   - Provide zero-TTL options for testing environments to avoid race conditions
   - Add helper utilities for clear cache invalidation when needed
   - Implement proper inspection of async methods to avoid mismatches

5. **Test Consolidation for Complete Coverage**
   - Analyze coverage reports to identify specific uncovered lines and branches
   - Combine complementary test files that cover different parts of the same functionality
   - Create targeted tests for specific edge cases that are missed by existing tests
   - Use descriptive test names that clearly indicate what scenario is being tested
   - Maintain all existing test functionality when consolidating test files
   - Focus on branch coverage for conditional logic, especially in financial calculations
   - Test both positive and negative scenarios for complete coverage
   - Verify coverage with specific coverage reports after changes

6. **Model Fixture Standardization**
   - Use naive_utc_now() for all database datetime fields instead of utc_now().replace(tzinfo=None)
   - Always use db_session.flush() instead of db_session.commit() in fixtures
   - Add comprehensive Args and Returns sections to all fixture docstrings
   - Use proper polymorphic classes (e.g., CheckingAccount) instead of base classes with type field
   - Never add helper functions to fixture files; add them to utility modules instead
   - Use fixture references for IDs instead of hardcoding values
   - Remove debug print statements from fixture code
   - Add proper type annotations for all parameters and return values
   - Standardize fixture naming conventions across all files
   - Organize fixtures by model type for better maintainability
   - Follow consistent patterns for relationship handling

7. **Utils Module Test Organization**
   - Organize tests into logical groupings based on functionality
   - Create separate test files for different aspects of a module (e.g., comparison, conversion, range operations)
   - Use descriptive test names that clearly indicate what's being tested
   - Document integration test candidates when unit tests aren't appropriate
   - Identify cross-layer concerns and document them for future refactoring
   - Maintain consistent test patterns across related functionality
   - Focus on behavior testing rather than implementation details
   - Document when integration tests are needed instead of using mocks

8. **Naive vs. Timezone-Aware Datetime Functions**
   - Use naive_* functions for database operations (e.g., naive_utc_now(), naive_days_ago())
   - Use timezone-aware functions for business logic (e.g., utc_now(), days_ago())
   - Convert between naive and aware only at the database boundary
   - Use clear variable naming to distinguish between naive and aware datetimes (e.g., db_date vs. aware_date)
   - Document the use of naive datetimes in function docstrings
   - Use naive functions when creating test fixtures for database models
   - Use timezone-aware functions when testing business logic
   - Be explicit about which type of datetime is expected in assertions

9. **Schema Factory Test Determinism**
   - Avoid random behavior in tests that can lead to intermittent failures
   - Use explicit parameters to control test behavior (e.g., include_seasonality)
   - Create separate test cases for different scenarios instead of random behavior
   - Implement proper test coverage for both positive and negative cases
   - Use random behavior tests only for verifying distribution, not for functional testing
   - Add clear parameter documentation to make test control obvious

10. **Repository Test Decoupling**
    - Create test-specific models and schemas for testing generic functionality
    - Avoid using business models in tests for generic components
    - Use schema factories to simplify test data creation
    - Follow the Arrange-Schema-Act-Assert pattern consistently
    - Create reusable test fixtures for common test scenarios
    - Implement proper validation flow in all repository tests

11. **Repository Fixture Organization**
    - Mirror source code directory structure in test fixtures
    - Use consistent naming convention with fixture_ prefix and _repositories suffix
    - Create separate fixture files for each repository type
    - Organize account type repositories in subdirectories matching source
    - Add proper docstrings with Args and Returns sections
    - Use dependency injection for related repositories
    - Register all fixture files in conftest.py
    - Maintain consistent formatting across all fixture files

12. **Schema Validation Patterns**
    - Separate field validation from model validation for better control flow
    - Use field validators for format and basic constraints
    - Use model validators for cross-field validation and business rules
    - Implement proper validation flow with field validators running first
    - Handle implicit field values in model validators
    - Add clear error messages for validation failures
    - Document validation behavior in docstrings
    - Test both field and model validation scenarios
