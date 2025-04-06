# Active Context: Debtonator

## Current Focus

Account Type Expansion, Service Layer Implementation, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation

### Recent Changes

1. **Implemented Hierarchical Error Handling for Account Types (April 5, 2025)** ✓
   - Created modular account-specific error hierarchy with proper inheritance
   - Implemented consistent naming convention with account type prefixes (e.g., CheckingOverdraftError)
   - Structured errors in modular directory matching domain model with proper `__init__.py` exports
   - Created base account error classes with standardized parameter handling
   - Applied "No Tech Debt" policy by fixing naming issues immediately

2. **Fixed UTC Timezone Validation and Datetime Handling Issues (April 5, 2025)** ✓
   - Fixed `LiabilityDateRange` validator to properly handle timezone-aware comparisons
   - Changed field validator to model validator with proper `ensure_utc()` calls
   - Fixed SQLAlchemy column validation to avoid direct boolean evaluation
   - Ensured all test classes use `utc_now()` instead of `datetime.now()` for default factories
   - Created missing `DepositScheduleResponse` schema with proper field definitions

3. **Implemented Service Layer for Account Types and Fixed Pydantic v2 Discriminated Union Issues (April 4, 2025)** ✓
   - Moved account type validation from schemas to service layer to resolve conflict with Pydantic discriminated unions
   - Enhanced feature flag integration in account creation and validation workflows
   - Implemented `get_banking_overview` and related methods for comprehensive financial data
   - Fixed polymorphic schema validation issues with discriminated unions in Pydantic v2
   - Added support for type-specific account handling via the feature flag-aware type registry system

4. **Implemented Repository Layer Tests for Account Types (April 3, 2025)** ✓
   - Created comprehensive integration tests for the modular repository pattern
   - Implemented tests for repository factory with dynamic module loading
   - Added tests for checking, savings, and credit account repositories
   - Created feature flag integration tests for banking account types
   - Added tests for bill splits with polymorphic account types

5. **Fixed Polymorphic Identity Warnings and Test Layer Separation (April 3, 2025)** ✓
   - Resolved SQLAlchemy warnings about incompatible polymorphic identity
   - Updated account fixtures to use proper polymorphic subclasses
   - Moved service-dependent tests from model unit tests to integration test files
   - Fixed test failures in CashflowForecast model tests
   - Added "Polymorphic Identity Pattern" section to system_patterns.md

## Next Steps

1. **Investigate Account Type Update Restrictions**
   - Evaluate architectural implications of updating account_type field
   - Account type changes affect DB storage location (polymorphic inheritance)
   - Consider implementing formal account type conversion workflow
   - Add validation at service layer to prevent direct account_type updates
   - Document account type transition policy in ADR

2. **Complete API Layer Integration**
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

1. **Testing Structured Directory Pattern**
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
