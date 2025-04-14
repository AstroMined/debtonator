# Active Context: Debtonator

## Current Focus

Account Type Expansion, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation, Schema Factory Testing, Error Handling System, UTC Datetime Compliance, Utils Module Test Coverage, Repository Test Pattern Implementation, API Layer Implementation, Test Infrastructure Improvement

### Recent Changes

1. **Fixed Repository Advanced Test Issues with Timezone Handling (April 14, 2025)** ✓
   - Improved datetime handling in repository tests in accordance with ADR-011:
     - Fixed `test_get_available_credit_trend` in balance history repository tests to handle timezone differences
     - Fixed `test_get_by_date_range` in payment schedules to properly compare dates with timezone awareness
     - Used proper utility functions from datetime_utils.py like `ensure_utc` for timezone compatibility
     - Implemented consistent datetime handling across repository layer
   - Enhanced schema validation for deposit schedules:
     - Fixed schema factory implementations to properly validate status fields
     - Removed hardcoded status validation in schema factories to let Pydantic handle validation
     - Ensured validation errors are properly raised and caught in tests
   - Fixed CreditAccount implementation issues:
     - Improved `update_balance` method to correctly handle available_credit calculation
     - Added safeguards for NULL available_credit values in tests
     - Enhanced test assertions to be more resilient to implementation details

2. **Fixed Bill Splits Integration with Standardized Terminology (April 14, 2025)** ✓
   - Standardized on "liability_id" terminology in bill split schema factories:
     - Updated `create_bill_split_schema` to consistently use `liability_id` parameter
     - Modified test files to use `liability_id` instead of `bill_id` to match schema
     - Updated parameter documentation for clarity
   - Implemented missing repository methods for bill splits:
     - Added `create_bill_splits` with automatic primary account split creation
     - Added `update_bill_splits` for existing splits with transaction support
     - Added `get_splits_by_bill` as an alias to maintain API compatibility
     - Added proper account validation and error handling
   - Enhanced transaction handling and validation:
     - Added transaction boundaries with proper rollback on errors
     - Implemented validation to prevent total splits exceeding bill amount
     - Added specific validation for non-existent accounts
     - Ensured all tests pass consistently

3. **Fixed Banking Account Type Implementations (April 14, 2025)** ✓
   - Added missing fixtures for credit and savings account types:
     - Created `test_credit_with_due_date` and `test_credit_with_rewards` fixtures
     - Created `test_savings_with_interest` and `test_savings_with_min_balance` fixtures
     - Fixed session handling for proper SQLAlchemy relationships
   - Fixed CreditAccount model fields:
     - Removed `total_limit` field which was causing compatibility issues
     - Added `last_statement_balance` field that was missing but referenced in schema
     - Added `rewards_rate` field for more accurate credit rewards tracking
   - Added specialized repository methods for credit and savings accounts:
     - Implemented utilization, statement status, and autopay query methods for credit accounts
     - Implemented interest rate, minimum balance, and yield query methods for savings accounts
     - Made sure methods have descriptive names that properly indicate account type
   - Fixed datetime timezone handling throughout the repository methods

4. **Fixed Schema-Model Field Mismatches in Account Hierarchy (April 14, 2025)** ✓
   - Removed credit-specific fields from base AccountBase schema:
     - Removed available_credit, total_limit, last_statement_balance, and last_statement_date
     - Removed corresponding field validators in both AccountBase and AccountUpdate
   - Added credit-specific fields to CreditAccount model:
     - Added available_credit field with proper Numeric type definition
     - Added total_limit field as an alias for credit_limit for backward compatibility
   - Updated CreditAccountBase schema to ensure all needed fields are explicitly included
   - Fixed test failures in checking_advanced.py related to schema-model mismatch
   - Improved object hierarchy design with better separation of concerns

5. **Refactored Repository Factory Tests (April 14, 2025)** ✓
   - Implemented generic test models instead of account-specific tests
   - Created test helper modules for type_a and type_b entities
   - Added comprehensive tests for polymorphic entity operations
   - Improved test structure with clear sections for core functionality
   - Enhanced test readability with consistent documentation patterns

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
