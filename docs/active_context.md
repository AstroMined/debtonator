# Active Context: Debtonator

## Current Focus

Account Type Expansion, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation, Schema Factory Testing, Error Handling System, UTC Datetime Compliance, Utils Module Test Coverage, Repository Test Pattern Implementation, API Layer Implementation, Test Infrastructure Improvement, Documentation Hierarchy Implementation

### Recent Changes

1. **Implemented Documentation Hierarchy for Test Helpers Directory (April 14, 2025)** ✓
   - Created comprehensive README.md files for test helpers and subdirectories:
     - Added README.md for repositories module with detailed documentation
     - Added README.md for repositories/test_types module with usage examples
     - Added README.md for test_data directory with file descriptions
     - Created properly structured feature_flag_utils module with README.md
   - Reorganized feature_flag_utils into proper module structure:
     - Moved utilities to dedicated directory with clear organization
     - Created proper __init__.py with exports for better usability
     - Added comprehensive documentation of utility functions
   - Updated main helpers README.md with complete structure:
     - Documented all helper categories with usage examples
     - Added cross-references to all subdirectory documentation
     - Ensured consistent documentation style across all files

2. **Completed Documentation for Multiple Test Directories (April 14, 2025)** ✓
   - Added README.md files for fixtures subdirectories:
     - Documented fixtures/api and fixtures/api/middleware directories
     - Created README.md for fixtures/models/account_types and banking subdirectory
     - Added documentation for fixtures/repositories/account_types hierarchy
     - Created README.md for fixtures/repositories/proxies directory
     - Added documentation for fixtures/services/interceptors and proxies
   - Created comprehensive README.md files for integration test directories:
     - Added documentation for integration/repositories/advanced hierarchy
     - Created README.md for integration/repositories/bill_splits directory
     - Added README.md for integration/repositories/crud and account_types subdirectories
   - Documented unit test directories:
     - Created README.md for unit/errors hierarchy with error class documentation
     - Added documentation for unit/registry directory
     - Created README.md for unit/utils and datetime_utils directories

3. **Fixed Account Type Test Organization (April 14, 2025)** ✓
   - Reorganized account type union tests:
     - Moved test_account_type_unions.py to banking-specific directory
     - Created banking-specific test_banking_account_type_unions.py
     - Updated imports and references in relevant files
   - Updated unit/schemas/account_types README.md with current architectural principles:
     - Documented polymorphic validation approach
     - Added information about discriminated unions
     - Clarified type-specific validation patterns
   - Enhanced integration/repositories README.md with recent improvements:
     - Updated information about passing tests
     - Added details about fixed account schema testing
     - Documented corrected datetime handling in tests

4. **Implemented Repository Test Documentation Improvements (April 14, 2025)** ✓
   - Updated repository test documentation for better guidance:
     - Added explicit four-step pattern documentation
     - Clarified schema factory usage in repository tests
     - Enhanced examples of polymorphic repository pattern usage
     - Added information about datetime handling compliance
   - Created consistent test organization documentation:
     - Documented separation between CRUD and advanced tests
     - Added file naming conventions and patterns
     - Created clear hierarchical organization of test files
   - Ensured proper cross-references between documentation files:
     - Added links to parent/child documentation
     - Referenced relevant ADRs and system patterns
     - Created clear navigation between related files

5. **Fixed Account Base Schema Testing to Align with Polymorphic Design (April 14, 2025)** ✓
   - Corrected account schema testing approach to align with architectural principles:
     - Removed incorrect expectation that base schema should validate type-specific fields
     - Added proper testing for discriminated unions in a dedicated test file
     - Documented the correct architectural approach in README.md
     - Fixed alignment between tests and polymorphic design principles
   - Enhanced type-specific validation testing:
     - Created test_account_type_unions.py test file
     - Added tests demonstrating proper field validation approach
     - Documented the intended validation pattern for account types
   - Reinforced the architectural principle that base schemas only validate universal fields

## Next Steps

1. **Continue Repository Test Refactoring**
   - Refactor account type advanced tests:
     - advanced/account_types/banking/test_ewa_advanced.py
     - advanced/account_types/banking/test_payment_app_advanced.py
   - Refactor other repository tests:
     - test_base_repository.py
     - test_factory.py
     - account_types/banking/test_checking.py
     - account_types/banking/test_credit.py
     - account_types/banking/test_savings.py

2. **Fix Remaining Schema-Model Mismatches**
   - Update CreditAccount model and schema to ensure all fields match
   - Fix same issues in related models like BNPLAccount and SavingsAccount
   - Add comprehensive tests for schema-model compatibility
   - Clean up backward compatibility fields as appropriate
   - Ensure field validation is in the correct layer

3. **Create Unit Tests for PolymorphicBaseRepository**
   - Implement test_polymorphic_base_repository.py to verify core functionality
   - Test disabled base methods raise proper exceptions
   - Test proper field filtering and validation
   - Create test scenarios for error handling cases
   - Verify proper registry integration
   - Create tests for update handling with type validation

4. **Complete Error Handling System Implementation**
   - Implement remaining error classes for account types
   - Create consistent error translation between layers
   - Add user-friendly error messages to API responses
   - Implement error handling middleware for API endpoints
   - Add comprehensive documentation for error handling patterns

5. **Implement API Layer for Account Types**
   - Create endpoint for GET /banking/overview
   - Implement endpoint for GET /banking/upcoming-payments
   - Add POST /accounts/banking endpoint
   - Create POST /accounts/bnpl/{account_id}/update-status endpoint
   - Add comprehensive documentation with OpenAPI annotations
   - Implement proper schema validation for API responses

## Implementation Lessons

1. **Proper Datetime Handling with ADR-011**
   - Always use the utility functions in datetime_utils.py for consistent timezone handling
   - Use `ensure_utc()` to guarantee timezone awareness when needed
   - Use `.replace(tzinfo=None)` for database operations as SQLAlchemy stores datetimes without timezone
   - For datetime comparisons, use `datetime_equals()` and `datetime_greater_than()` with `ignore_timezone=True`
   - Be cautious with timestamps in tests to ensure proper date range filtering and comparisons
   - Understand the distinction between naive datetimes (for DB) and timezone-aware datetimes (for business logic)

2. **Schema-Model Field Alignment**
   - Keep model fields and schema fields aligned to prevent runtime errors
   - Validate that model fields can accept values from schema fields
   - Consider creating utility tools to verify schema-model compatibility
   - Move type-specific fields to the appropriate subclass schemas
   - Be careful about backward compatibility fields that could cause issues
   - Consider using field validation at the schema level for type-specific fields
   - Use proper inheritance patterns in both models and schemas
   - Ensure proper separation of concerns in the class hierarchy

3. **Schema Factory Implementation Best Practices**
   - Don't silently "fix" invalid input in schema factories - let validation handle it
   - Schema factories should construct valid data structures but not perform validation
   - Let schema validation be handled by the actual schema classes for consistent errors
   - Don't override validation logic in factories - it creates inconsistencies
   - Document expected schema structure clearly in factory function docstrings
   - Consider adding test utility assertions specifically for schema validation

4. **Repository Test Design**
   - Focus on testing behavior, not implementation details
   - Use flexible assertions that can handle minor implementation changes
   - Verify expected values rather than exact implementation details (e.g. check credit values, not timestamps)
   - Use appropriate helper functions from utility modules
   - Make tests more robust by handling edge cases like NULL values
   - For date-based tests, be explicit about timezone handling
   - Test functionality through existing methods rather than adding specialized ones

5. **Polymorphic Repository Pattern**
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
   - Preserve optional fields with existing values during partial updates
   - Skip setting optional fields to NULL if they already have a value
