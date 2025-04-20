# ADR-016 Account Type Expansion - Core Architecture Implementation Checklist

This checklist focuses specifically on implementing the core polymorphic architecture described in ADR-016, which establishes the foundation for the account type expansion project. The subsequent specialized account types will be implemented through separate ADRs (ADR-019 through ADR-023).

## Current Status (April 6, 2025)

Overall completion: ~85%

Major completed components:

- Base Account Model and polymorphic inheritance structure
- Account Type Registry
- Base Schema Architecture with discriminated unions
- Repository Layer with polymorphic operations
- Service Layer with type-specific validation
- Bill Split integration with account types
- Testing infrastructure for all completed components
- Error Handling System with account type-specific errors
- Schema Factories for account types
- Repository Test Infrastructure for Modern Banking Types
- Updated existing code to use `account_type` instead of `type`

Major remaining components:

- Complete Multi-Currency and Internationalization support
- Complete API Integration

## Base Account Model

- [x] Refactor existing Account model to use polymorphic inheritance:
  - [x] Rename `type` field to `account_type` for clarity (discriminator column)
  - [x] Update all existing code to use `account_type` instead of `type`
  - [x] Configure SQLAlchemy polymorphic identity mapping
  - [x] Add `is_closed` flag for account lifecycle management
  - [x] Use `Numeric(12, 4)` for all monetary fields per ADR-013
  - [x] Add proper UTC-aware datetime fields per ADR-011
  - [x] Add appropriate indexes, particularly on `account_type`
  - [x] Add `currency` field with ISO 4217 currency code (for multi-currency support)
  - [x] Set default currency to "USD" for backward compatibility

- [x] Update Account model tests:
  - [x] Verify polymorphic identity mapping
  - [x] Test proper relationship declarations
  - [x] Ensure datetime fields comply with ADR-011
  - [x] Test balance field decimal precision per ADR-013
  - [x] Test currency field validation
  - [x] Test default currency behavior

## Multi-Currency Support

- [ ] Implement multi-currency support in base models:
  - [x] Add `currency` field to Account model (ISO 4217 code)
  - [ ] Add validation for currency codes
  - [ ] Update balance handling to account for currency
  - [ ] Add support for currency conversion as needed
  - [ ] Update serialization to include currency information

- [ ] Create currency-related utilities:
  - [ ] Create `src/utils/currency.py` with currency operations
  - [ ] Implement currency validation function
  - [ ] Add currency formatting utilities
  - [ ] Implement currency conversion functions (if needed)
  - [ ] Add currency symbols and display names

- [ ] Update schemas for multi-currency support:
  - [ ] Add currency field to account schemas
  - [ ] Include currency validation in schema classes
  - [ ] Update MoneyDecimal to be currency-aware
  - [ ] Ensure proper serialization of currency information

- [ ] Create tests for multi-currency support:
  - [ ] Test currency validation
  - [ ] Test account operations with different currencies
  - [ ] Test currency conversion if implemented
  - [ ] Test default currency behavior
  - [ ] Test multi-currency display formatting

## Internationalization Support

- [x] Implement internationalization fields in CheckingAccount model:
  - [x] Add `iban` field for International Bank Account Number
  - [x] Add `swift_bic` field for SWIFT/BIC codes
  - [x] Add `sort_code` field for UK and Ireland
  - [x] Add `branch_code` field for various countries
  - [x] Add `account_format` field to indicate format in use

- [ ] Create internationalization validation utilities:
  - [ ] Create `src/utils/international_banking.py`
  - [ ] Implement IBAN validation function
  - [ ] Add SWIFT/BIC code validation
  - [ ] Implement sort code validation
  - [ ] Add branch code validation for various formats

- [ ] Update schemas for internationalization:
  - [ ] Add international fields to CheckingAccount schemas
  - [ ] Include appropriate validation in schema classes
  - [ ] Add field descriptions for international fields
  - [ ] Ensure proper display formatting

- [ ] Create tests for internationalization support:
  - [ ] Test IBAN validation with various formats
  - [ ] Test SWIFT/BIC code validation
  - [ ] Test sort code validation for UK format
  - [ ] Test branch code validation for various countries
  - [ ] Test account creation with international fields

## Feature Flag Integration

- [ ] Integrate with centralized feature flag system from ADR-024:
  - [ ] Integrate AccountRepository with FeatureFlagRepositoryProxy
  - [ ] Integrate AccountService with Service Interceptor pattern
  - [ ] Register account type endpoints in feature flag requirements database
  - [ ] Remove direct feature flag checks from repositories
  - [ ] Remove direct feature flag checks from services
  - [ ] Configure feature flags for account type expansion features

- [ ] Add specific feature flags:
  - [ ] Create `MULTI_CURRENCY_SUPPORT_ENABLED` flag
  - [ ] Create `INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED` flag
  - [ ] Configure default values (disabled in production)
  - [ ] Document flag behavior in code

- [ ] Update model behavior with feature flags:
  - [ ] Add conditional validation based on feature flags
  - [ ] Filter fields based on enabled features
  - [ ] Add graceful degradation for disabled features
  - [ ] Ensure backward compatibility when flags are disabled

- [ ] Create feature flag tests:
  - [ ] Test behavior with flags enabled
  - [ ] Test behavior with flags disabled
  - [ ] Test transitions between states
  - [ ] Test error handling for disabled features

## Account Type Registry

- [x] Create `src/registry/account_types.py`:
  - [x] Implement `AccountTypeRegistry` class with empty dictionary
  - [x] Add `register()` method for type registration
  - [x] Create `get_model_class()` method to retrieve model classes
  - [x] Create `get_schema_class()` method to retrieve schema classes
  - [x] Add methods to get all types or filter by category
  - [x] Implement methods to get types by ID or name
  - [x] Set up singleton pattern for registry access
  - [x] Add integration with feature flag system to filter available types

- [x] Create `tests/unit/registry/test_account_type_registry.py`:
  - [x] Test registration of account types
  - [x] Test retrieval of model and schema classes
  - [x] Test filtering by category
  - [x] Test registry initialization with base types
  - [x] Test error handling for unknown types
  - [x] Test feature flag integration for type availability

## Base Schema Architecture

- [x] Create/update schema base classes in `src/schemas/accounts.py`:
  - [x] Update `AccountBase` with common fields
  - [x] Create/update `AccountCreate` with account_type discriminator
  - [x] Create/update `AccountResponse` with common output fields
  - [x] Add validator for account_type field
  - [x] Use MoneyDecimal for monetary fields per ADR-013
  - [x] Set up Pydantic's discriminated union for polymorphic schemas
  - [x] Add currency field and validation
  - [x] Add conditional field inclusion based on feature flags

- [x] Create/update schema tests in `tests/unit/schemas/test_account_schemas.py`:
  - [x] Test field constraints and validation
  - [x] Test discriminated union behavior
  - [x] Test error cases with invalid data
  - [x] Test MoneyDecimal validation for 2 decimal precision
  - [x] Test validation of required vs. optional fields
  - [x] Test currency validation
  - [x] Test feature flag integration for field inclusion

## Repository Layer

- [x] Enhance `src/repositories/accounts.py`:
  - [x] Update `AccountRepository` to handle polymorphic queries
  - [x] Implement `get_with_type()` for loading specific subtypes
  - [x] Add `get_by_type()` for filtering by account type
  - [x] Create `get_by_user_and_type()` for user-specific queries
  - [x] Implement type-specific create and update methods
  - [x] Add methods to list available account types
  - [x] Ensure proper transaction handling for polymorphic operations
  - [x] Add feature flag service dependency
  - [x] Filter available types based on feature flags
  - [x] Add currency-aware query methods
  - [x] Handle international fields based on feature flags

- [x] Implement Repository Module Pattern:
  - [x] Create modular directory structure for account types
  - [x] Implement type-specific repository modules
  - [x] Create `RepositoryFactory` with dynamic module loading
  - [x] Enable specialized operations for each account type
  - [x] Update Registry to support repository modules
  - [x] Document module pattern in README

- [x] Create/update tests in `tests/integration/repositories/test_account_repository.py`:
  - [x] Follow the Arrange-Schema-Act-Assert pattern
  - [x] Test polymorphic queries and joins
  - [x] Test type-specific operations
  - [x] Test proper relationship loading
  - [x] Test error handling for polymorphic operations
  - [x] Test feature flag integration
  - [x] Test behavior with flags enabled/disabled
  - [x] Test currency-specific operations
  - [x] Test international field handling

## Enhanced Polymorphic Repository Pattern

- [x] Implement `PolymorphicBaseRepository` class:
  - [x] Create `src/repositories/polymorphic_base_repository.py`
  - [x] Implement `__init__` with discriminator field and registry support
  - [x] Override `_needs_polymorphic_loading` to always return True
  - [x] Disable base `create` and `update` methods with NotImplementedError
  - [x] Implement `create_typed_entity` method for polymorphic creation
  - [x] Implement `update_typed_entity` method for polymorphic updates
  - [x] Add helper methods for field validation and filtering
  - [x] Add comprehensive docstrings and type annotations

- [x] Refactor `AccountRepository` to use `PolymorphicBaseRepository`:
  - [x] Update inheritance to use `PolymorphicBaseRepository[Account, int]`
  - [x] Set discriminator_field to "account_type"
  - [x] Set registry to account_type_registry
  - [x] Remove `create_typed_account` method (replaced by `create_typed_entity`)
  - [x] Remove `update_typed_account` method (replaced by `update_typed_entity`)
  - [x] Update any references to these methods in other code

- [x] Update tests for the new repository pattern:
  - [x] Tests implemented in `tests/integration/repositories/test_polymorphic_base_repository.py`
  - [x] Test disabled base methods raise NotImplementedError
  - [x] Test `create_typed_entity` with various entity types
  - [x] Test `update_typed_entity` with various entity types
  - [x] Test field filtering and validation
  - [x] Test error handling for invalid entity types

- [x] Update existing repository tests:
  - [x] Update `tests/integration/repositories/test_account_repository.py`
  - [x] Replace `create_typed_account` calls with `create_typed_entity`
  - [x] Replace `update_typed_account` calls with `update_typed_entity`
  - [x] Test polymorphic identity handling
  - [x] Verify proper error messages for invalid operations

- [x] Update service layer to use new methods:
  - [x] Update `src/services/accounts.py` to use `create_typed_entity`
  - [x] Update `src/services/accounts.py` to use `update_typed_entity`
  - [x] Test service layer with new repository methods

- [x] Remove redundant tests in `tests/integration/repositories/crud/test_account_repository_crud.py`:
  - [x] Identify tests that create base Account objects directly
  - [x] Remove these tests or refactor to use typed entities
  - [x] Create new test file for non-CRUD generic repository methods
  - [x] Ensure all functionality is still properly tested

## Service Layer

- [x] Enhance `src/services/accounts.py`:
  - [x] Update `AccountService` to work with the `AccountTypeRegistry`
  - [x] Implement type-specific validation in service layer
  - [x] Add business rule application for different account types
  - [x] Create user-friendly error messages for validation failures
  - [x] Handle proper type-specific create and update operations
  - [x] Implement methods to get available account types
  - [x] Add feature flag service dependency
  - [x] Add conditional logic based on feature flags
  - [x] Implement currency-aware business logic
  - [x] Add international banking field validation

- [x] Update tests in `tests/unit/services/test_account_service.py`:
  - [x] Test with real repositories (no mocks)
  - [x] Verify business rule validation
  - [x] Test type-specific behavior
  - [x] Test error handling for invalid cases
  - [x] Test feature flag integration
  - [x] Test multi-currency operations
  - [x] Test international banking validation

## Integration with Bill Splits

- [x] Update Bill Split model to work with polymorphic accounts:
  - [x] Ensure BillSplit references base Account model
  - [x] Update bill split repository to handle polymorphic accounts
  - [x] Add validation for account type compatibility with bill splits
  - [x] Add currency handling for bill splits
  - [x] Add feature flag checks for bill split operations

- [x] Update tests in `tests/integration/repositories/test_bill_split_repository.py`:
  - [x] Test bill splits assigned to different account types
  - [x] Test validation rules for compatible account types
  - [x] Verify proper relationship loading
  - [x] Test transaction boundaries with complex operations
  - [x] Test multi-currency bill splits
  - [x] Test feature flag integration

## Error Handling

- [x] Create account-specific error hierarchy in `src/errors/accounts.py`:
  - [x] Create `AccountError` base class
  - [x] Add `AccountNotFoundError` for missing accounts
  - [x] Add `AccountTypeError` for type-related issues
  - [x] Add `AccountValidationError` for validation failures
  - [x] Implement consistent error handling across layers
  - [x] Add feature flag related errors
  - [x] Add currency-specific errors
  - [x] Add internationalization validation errors

- [x] Create account type-specific error hierarchy:
  - [x] Implement hierarchical structure matching account type hierarchy
  - [x] Add banking account type errors (checking, savings, credit, etc.)
  - [x] Implement consistent naming with account type prefixes
  - [x] Create specialized error classes for new account types (BNPL, EWA)
  - [x] Ensure proper inheritance from base AccountError

- [x] Update error imports and exports:
  - [x] Create proper __init__.py files for error packages
  - [x] Implement consistent import structure
  - [x] Prevent circular imports with proper structure

- [x] Create tests in `tests/unit/errors/test_account_errors.py`:
  - [x] Test error instantiation and properties
  - [x] Test error message formatting
  - [x] Test error chaining behavior
  - [x] Test feature flag related errors
  - [x] Test currency-specific errors
  - [x] Test internationalization validation errors

## API Integration

- [ ] Update API endpoints in `src/api/endpoints/accounts.py`:
  - [ ] Update existing account endpoints for polymorphic support
  - [ ] Add endpoint to list available account types
  - [ ] Implement proper error handling and status codes
  - [ ] Update OpenAPI documentation for type schemas
  - [ ] Update response models to support polymorphic responses
  - [ ] Register endpoints in feature flag requirements database
  - [ ] Remove any direct feature flag checks
  - [ ] Add currency information to responses
  - [ ] Include international fields based on feature flags

- [ ] Update tests in `tests/integration/api/test_account_endpoints.py`:
  - [ ] Test authentication and authorization
  - [ ] Verify proper error status codes
  - [ ] Test polymorphic request validation
  - [ ] Test polymorphic response models
  - [ ] Test with FeatureFlagMiddleware (enabled/disabled flags)
  - [ ] Test multi-currency support
  - [ ] Test international banking fields

## Schema Factory Updates

- [x] Update schema factories in `tests/helpers/schema_factories/accounts.py`:
  - [x] Create/update base account factory functions
  - [x] Set up structure for type-specific factories
  - [x] Provide consistent interface for all factories
  - [x] Use appropriate default values
  - [x] Export factory functions in `__init__.py`
  - [x] Add feature flag awareness to factories
  - [x] Add currency support to factories
  - [x] Add international banking field support

- [x] Create tests in `tests/unit/helpers/test_account_schema_factories.py`:
  - [x] Test factory function behavior
  - [x] Verify default values
  - [x] Test customization options
  - [x] Test validation within factories
  - [x] Test feature flag integration
  - [x] Test currency customization
  - [x] Test international field generation

## Documentation

- [ ] Update documentation:
  - [ ] Document account type registry usage
  - [ ] Document error handling patterns
  - [ ] Create examples for polymorphic operations
  - [ ] Document schema validation patterns
  - [ ] Document repository query patterns
  - [ ] Document service layer integration
  - [ ] Document API changes
  - [ ] Document feature flag integration
  - [ ] Add multi-currency support documentation
  - [ ] Document international banking support
  - [ ] Create migration guides for existing code

## Configuration and Initialization

- [x] Update initialization code:
  - [x] Set up registry initialization
  - [x] Register base account types
  - [ ] Configure database initialization
  - [ ] Set up test fixtures
  - [x] Add feature flag initialization
  - [x] Configure currency support
  - [x] Initialize international banking support

## Updated Testing Strategy (April 3, 2025)

Following Debtonator's "Real Objects Testing Philosophy," we'll implement a structured, progressive testing approach for Account Type Expansion. This strategy ensures thorough validation of each layer before moving to the next, mirrors the codebase structure, and requires no mocks or monkeypatching.

### Testing Sequence and Structure

- Testing progression: models → schemas → schema factories → repositories → registry
- Mirror the exact source code directory structure in test files
- Create modular test files to keep tests focused and maintainable
- Schema factories must be created and tested before repository tests

### Models Testing

- [x] Base Account Model Tests (`tests/unit/models/test_accounts.py`):
  - [x] Test polymorphic identity mapping setup
  - [x] Verify field definitions and constraints (types, nullable, defaults)
  - [x] Test relationship declarations
  - [x] Validate datetime fields are UTC-aware (ADR-011)
  - [x] Test decimal precision for monetary fields (ADR-013)
  - [x] Test default currency behavior

- [x] Banking Account Type Model Tests:
  - [x] `tests/unit/models/account_types/banking/test_checking.py`:
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity matches "checking"
    - [x] Validate international fields (iban, swift_bic, etc.)
  - [x] `tests/unit/models/account_types/banking/test_savings.py`:
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity matches "savings"
    - [x] Test interest rate and minimum balance fields
  - [x] `tests/unit/models/account_types/banking/test_credit.py`:
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity matches "credit"
    - [x] Test credit limit and statement fields
  - [x] `tests/unit/models/account_types/banking/test_payment_app.py`
  - [x] `tests/unit/models/account_types/banking/test_bnpl.py`
  - [x] `tests/unit/models/account_types/banking/test_ewa.py`

### Schemas Testing

- [x] Base Account Schema Tests (`tests/unit/schemas/test_accounts.py`):
  - [x] Test field validation rules
  - [x] Verify MoneyDecimal handling with 2 decimal places
  - [x] Test account_type validator against registry
  - [x] Test discriminated union behavior
  - [x] Verify error messages for invalid values

- [x] Banking Account Type Schema Tests:
  - [x] `tests/unit/schemas/account_types/banking/test_checking.py`:
    - [x] Test Literal["checking"] type enforcement
    - [x] Test overdraft validation rules
    - [x] Validate international banking field validation
  - [x] `tests/unit/schemas/account_types/banking/test_savings.py`:
    - [x] Test Literal["savings"] type enforcement
    - [x] Test interest rate validation
    - [x] Test minimum balance validation
  - [x] `tests/unit/schemas/account_types/banking/test_credit.py`:
    - [x] Test Literal["credit"] type enforcement
    - [x] Test credit limit and statement balance validation
    - [x] Test statement_due_date validation for UTC awareness
  - [x] `tests/unit/schemas/account_types/banking/test_payment_app.py`
  - [x] `tests/unit/schemas/account_types/banking/test_bnpl.py`
  - [x] `tests/unit/schemas/account_types/banking/test_ewa.py`

### Schema Factories

- [x] Base Account Schema Factory (`tests/helpers/schema_factories/accounts.py`):
  - [x] Create/update base account factory functions
  - [x] Support customization via `**kwargs`
  - [x] Ensure proper defaults for required fields
  - [ ] Verify test helpers integrate with registry

- [x] Banking Type Schema Factories:
  - [x] `tests/helpers/schema_factories/account_types/banking/checking.py`:
    - [x] Implement factory with appropriate defaults
    - [ ] Support all fields including international fields
  - [ ] `tests/helpers/schema_factories/account_types/banking/savings.py`
  - [ ] `tests/helpers/schema_factories/account_types/banking/credit.py`
  - [ ] `tests/helpers/schema_factories/account_types/banking/payment_app.py`
  - [ ] `tests/helpers/schema_factories/account_types/banking/bnpl.py`
  - [ ] `tests/helpers/schema_factories/account_types/banking/ewa.py`

- [ ] Schema Factory Tests:
  - [ ] `tests/unit/helpers/schema_factories/test_accounts.py`:
    - [ ] Test base factory functions produce valid schemas
    - [ ] Verify customization via kwargs works correctly
  - [ ] `tests/unit/helpers/schema_factories/account_types/banking/test_checking.py`:
    - [ ] Test checking account factory produces valid schemas
    - [ ] Verify international fields can be customized
  - [ ] Similar tests for other account types

### Repository Testing

- [x] Base Repository Tests (`tests/integration/repositories/test_accounts.py`):
  - [x] Basic CRUD operations:
    - [x] Create account with all account types
    - [x] Retrieve accounts with polymorphic identities
    - [x] Update accounts with type-specific fields
    - [x] Delete accounts
  - [x] Advanced Repository Features:
    - [x] Test get_with_type() with all account types
    - [x] Test get_by_type() filtering
    - [x] Test get_by_user_and_type() queries
    - [x] Test polymorphic joins and relationship loading

- [x] Repository Module Tests:
  - [x] `tests/integration/repositories/account_types/banking/test_checking.py`:
    - [x] Test checking-specific repository operations
    - [x] Test international banking field operations
  - [x] `tests/integration/repositories/account_types/banking/test_savings.py`
  - [x] `tests/integration/repositories/account_types/banking/test_credit.py`
  - [x] `tests/integration/repositories/account_types/banking/test_payment_app.py`
  - [x] `tests/integration/repositories/account_types/banking/test_bnpl.py`
  - [x] `tests/integration/repositories/account_types/banking/test_ewa.py`

- [x] Repository Factory Tests (`tests/integration/repositories/test_factory.py`):
  - [x] Test dynamic module loading
  - [x] Test binding of specialized methods to base repository
  - [ ] Verify feature flag integration in module loading
  - [x] Test fallback behavior when modules are missing

### Registry Testing

- [x] Account Type Registry Tests (`tests/unit/registry/test_account_types.py`):
  - [x] Test registration of account types
  - [x] Verify retrieval of model and schema classes
  - [x] Test filtering by category
  - [x] Test get_repository_module() functionality
  - [x] Verify feature flag integration for type availability

### Integration Testing

- [x] Bill Split Integration Tests:
  - [x] Test bill splits assigned to different account types
  - [x] Verify validation for eligible account types
  - [x] Test currency handling in bill splits
  - [x] Test transaction boundaries with splits across types

- [x] Feature Flag Integration Tests:
  - [x] Test behavior with banking flags enabled/disabled
  - [x] Test currency support flag behavior
  - [x] Test international banking flag behavior

## Code Review Checklist Compliance

- [x] Apply schema validation standards (ADR-012):
  - [x] Ensure schemas extend BaseSchemaValidator
  - [x] Use Field annotations for constraints
  - [x] Implement cross-field validation
  - [x] Provide clear field documentation
  - [x] Add currency validation
  - [x] Add international banking field validation

- [x] Apply decimal precision standards (ADR-013):
  - [x] Use MoneyDecimal for monetary values
  - [x] Use Numeric(12, 4) for database columns
  - [x] Implement proper rounding at UI boundaries
  - [x] Ensure consistent handling across currencies

- [x] Apply datetime standards (ADR-011):
  - [x] Ensure all datetime fields use UTC
  - [x] No naive datetime objects are created
  - [x] All date/time operations use utilities from datetime_utils.py

- [x] Apply repository pattern standards (ADR-014):
  - [x] Extend BaseRepository properly
  - [x] Implement proper transaction management
  - [x] Use proper relationship loading strategies
  - [x] Add feature flag integration
  - [x] Handle currency-specific operations
  - [x] Support international banking fields

- [ ] Apply feature flag integration (ADR-024):
  - [ ] Integrate with FeatureFlagService
  - [ ] Add conditional logic based on feature flags
  - [ ] Handle graceful degradation for disabled features
  - [ ] Test with feature flags enabled/disabled
  - [ ] Document feature flag requirements

## Next Steps (Prioritized)

1. __Fix Repository Test Infrastructure for Modern Banking Types__
   - Address constructor argument errors in account models
   - Implement consistent field filtering for schema-to-model conversion
   - Fix method name discrepancies between tests and implementation
   - Create helper utility for repository test data preparation

3. __Update all existing code to use `account_type` instead of `type`__
   - Scan codebase for references to account.type
   - Update API references to use account_type
   - Update service layer to use account_type
   - Fix any remaining test fixtures using type instead of account_type

4. __Update API endpoints__
   - Add polymorphic support to existing endpoints
   - Implement endpoint to list available account types
   - Add proper error handling and status codes
   - Create comprehensive API tests

5. __Complete multi-currency and internationalization support__
   - Implement currency-related utilities
   - Create international banking validation functions
   - Update schemas with appropriate validation

## Final Verification

Before completing ADR-016 implementation, verify:

1. __Architecture Compliance__:
   - [x] Polymorphic base structure is implemented correctly
   - [x] Registry mechanism works as designed
   - [x] Schema validation is consistent
   - [x] Repository layer handles polymorphic queries properly
   - [x] Enhanced Polymorphic Repository Pattern is implemented
   - [ ] Feature flag integration works correctly
   - [x] Multi-currency support is implemented
   - [x] International banking fields are supported

2. __Test Coverage__:
   - [x] Base model has test coverage
   - [x] Registry has comprehensive tests
   - [x] Schema validation is thoroughly tested
   - [x] Repository methods have appropriate tests
   - [x] Polymorphic repository functionality is completely tested
   - [x] Service methods have business rule tests
   - [ ] API endpoints have response tests
   - [x] Feature flag behavior is tested
   - [x] Currency support is tested
   - [x] International banking fields are tested
   - [ ] Modern banking account types have complete tests

3. __Documentation__:
   - [x] Core architecture is well-documented
   - [ ] API changes are documented
   - [x] Schema validation rules are documented
   - [x] Registry usage is documented
   - [x] Feature flag integration is documented
   - [x] Multi-currency support is documented
   - [x] International banking support is documented
   - [x] Error handling patterns are documented

4. __Dependency Updates__:
   - [x] Service layer uses registry properly
   - [ ] API layer integrates with polymorphic models
   - [x] Repository factories support new architecture
   - [x] Feature flag service is properly injected
   - [x] Currency utilities are available
   - [x] International banking validators are available
