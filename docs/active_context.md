# Active Context: Debtonator

## Current Focus

Account Type Expansion, Service Layer Implementation, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation

### Recent Changes

1. **Fixed AccountUpdate Schema and Test Infrastructure (April 6, 2025)** ✓
   - Removed id field from AccountUpdate schema as it's not part of update data
   - Fixed test assertions to match schema structure
   - Added proper credit-specific field validation tests
   - Enhanced test coverage for account type validation
   - Fixed integration test to handle account ID correctly

2. **Fixed Test Infrastructure for Modern Banking Account Types (April 6, 2025)** ✓
   - Added feature_flag_service fixture with test initialization and database setup
   - Fixed repository test method calls from get_by_id() to get() for consistency
   - Identified and addressed constructor argument errors with field filtering
   - Updated conftest.py to include modern banking account fixtures
   - Fixed schema validation issue with card_last_four when has_debit_card is false

3. **Implemented Schema Factories with ADR-011 Compliance (April 5, 2025)** ✓
   - Refactored schema factory tests into modular files by account type
   - Fixed datetime handling to use `utc_now()` and `utc_datetime()` utils for ADR-011 compliance
   - Ensured proper datetime timezone-aware handling across all schema factories
   - Modularized test structure to match source code organization
   - Updated implementation checklists for ADRs 016, 019, and 024

4. **Implemented Hierarchical Error Handling for Account Types (April 5, 2025)** ✓
   - Created modular account-specific error hierarchy with proper inheritance
   - Implemented consistent naming convention with account type prefixes (e.g., CheckingOverdraftError)
   - Structured errors in modular directory matching domain model with proper `__init__.py` exports
   - Created base account error classes with standardized parameter handling
   - Applied "No Tech Debt" policy by fixing naming issues immediately

5. **Fixed UTC Timezone Validation and Datetime Handling Issues (April 5, 2025)** ✓
   - Fixed `LiabilityDateRange` validator to properly handle timezone-aware comparisons
   - Changed field validator to model validator with proper `ensure_utc()` calls
   - Fixed SQLAlchemy column validation to avoid direct boolean evaluation
   - Ensured all test classes use `utc_now()` instead of `datetime.now()` for default factories
   - Created missing `DepositScheduleResponse` schema with proper field definitions

## Next Steps

1. **Investigate Repository Layer Test Architecture**
   - Identify better approach to handle schema-to-model field mapping
   - Address "available_credit" field-filtering issue across all tests
   - Determine if a common test utility would reduce code duplication
   - Evaluate if repository tests should validate constructor arg filtering
   - Consider architectural changes to prevent these issues long-term

2. **Investigate Account Type Update Restrictions**
   - Evaluate architectural implications of updating account_type field
   - Account type changes affect DB storage location (polymorphic inheritance)
   - Consider implementing formal account type conversion workflow
   - Add validation at service layer to prevent direct account_type updates
   - Document account type transition policy in ADR

3. **Complete API Layer Integration**
   - Implement GET /banking/overview endpoint
   - Create GET /banking/upcoming-payments endpoint
   - Add POST /accounts/banking endpoint
   - Implement POST /accounts/bnpl/{account_id}/update-status endpoint
   - Create endpoints to retrieve available account types

3. **Complete API Layer Tests**
   - Create integration tests for API endpoints with all account types
   - Test polymorphic request and response validation
   - Implement tests for feature flag integration at API layer
   - Add tests for error handling and status codes

4. **Update Test Cases for Polymorphic Validation**
   - Extend test coverage for the new Pydantic v2 discriminated union pattern
   - Create comprehensive test cases for all account types
   - Test proper handling of inheritance and discriminator fields

5. **Complete Schema Factory Development**
   - Implement schema factories for all account types
   - Add support for customization via kwargs
   - Create factories for testing with appropriate defaults
   - Support international banking field generation

## Implementation Lessons

1. **Repository Field Filtering Pattern**
   - Schema-generated data may include fields not in model constructors
   - Field filtering should happen before model instantiation in repositories
   - Consider using type-aware field filtering in repository layer
   - Alternatively, use schema_to_model() functions to handle conversion
   - Balance between flexibility and maintenance when handling field mapping

2. **Testing Structured Directory Pattern**
   - Mirror the exact source directory structure in test files
   - Separate test files per component keeps tests focused and maintainable
   - Use descriptive test method names that describe the behavior being tested
   - Create proper test package structure with `__init__.py` files

2. **Polymorphic Schema Pattern with Pydantic V2**
   - Use Literal fields to enforce discriminator values in derived schemas
   - Use Annotated with Union and Field(discriminator=) for polymorphic API schemas
   - With discriminated unions, client only needs to set account_type and other fields
   - Always document discriminator field usage in schema docstrings

3. **Feature Flag Layer Integration**
   - Feature flags should be evaluated at the service layer, not directly in repositories
   - Integration tests for feature flags should test full flow from config to database
   - Design feature flags to handle context-specific evaluation
   - Test both enabled and disabled states for proper flag behavior

4. **Discriminator Field Validator Pattern**
   - Move validators away from discriminator fields to prevent conflict with Pydantic v2
   - For discriminated unions, validators cannot operate on the discriminator field
   - Move complex validation logic to the service layer
   - Use Literal types to enforce discriminator values in schema classes

5. **Real Objects Testing Philosophy**
   - Never use mocks in tests - unittest.mock and MagicMock are strictly prohibited
   - Always use real repositories with the test database
   - Test database gets set up and torn down between each test
   - Test real cross-layer interactions instead of isolating components

6. **Type-Specific Validator Methods**
   - Implement cross-field validation using model validators
   - Validate complex business rules at the model level, not individual fields
   - Use validation context (info.data) to access other field values
   - Always check for None values to handle partial updates

7. **Safe Datetime Comparison**
   - Use `ensure_utc()` to normalize datetimes before comparison
   - Use model validators instead of field validators for cross-field validation
   - Ensure all datetime comparisons handle timezone-aware and naive objects properly
   - Follow ADR-011 recommendations consistently across the codebase

8. **Repository Method Naming Consistency**
   - Use consistent method names across repository implementations
   - Prefer get() over get_by_id() for primary key retrieval
   - Standardize method signatures across repository hierarchy
   - Document method name expectations in repository interfaces
   - Use factory methods to abstract creation details from consumers
