# ADR-016 Account Type Expansion - Core Architecture Implementation Checklist

This checklist focuses specifically on implementing the core polymorphic architecture described in ADR-016, which establishes the foundation for the account type expansion project. The subsequent specialized account types will be implemented through separate ADRs (ADR-019 through ADR-023).

## Base Account Model

- [x] Refactor existing Account model to use polymorphic inheritance:
  - [x] Rename `type` field to `account_type` for clarity (discriminator column)
  - [ ] Update all existing code to use `account_type` instead of `type`
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

- [ ] Integrate with feature flag system from ADR-024:
  - [ ] Add feature flag support to AccountRepository
  - [ ] Add feature flag support to AccountService
  - [ ] Add feature flag checks to API endpoints
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

- [x] Create feature flag tests:
  - [x] Test behavior with flags enabled
  - [x] Test behavior with flags disabled
  - [x] Test transitions between states
  - [x] Test error handling for disabled features

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

- [ ] Create `tests/unit/registry/test_account_type_registry.py`:
  - [ ] Test registration of account types
  - [ ] Test retrieval of model and schema classes
  - [ ] Test filtering by category
  - [ ] Test registry initialization with base types
  - [ ] Test error handling for unknown types
  - [ ] Test feature flag integration for type availability

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

- [ ] Create account-specific error hierarchy in `src/errors/accounts.py`:
  - [ ] Create `AccountError` base class
  - [ ] Add `AccountNotFoundError` for missing accounts
  - [ ] Add `AccountTypeError` for type-related issues
  - [ ] Add `AccountValidationError` for validation failures
  - [ ] Implement consistent error handling across layers
  - [ ] Add feature flag related errors
  - [ ] Add currency-specific errors
  - [ ] Add internationalization validation errors

- [ ] Create tests in `tests/unit/errors/test_account_errors.py`:
  - [ ] Test error instantiation and properties
  - [ ] Test error message formatting
  - [ ] Test error chaining behavior
  - [ ] Test feature flag related errors
  - [ ] Test currency-specific errors
  - [ ] Test internationalization validation errors

## API Integration

- [ ] Update API endpoints in `src/api/endpoints/accounts.py`:
  - [ ] Update existing account endpoints for polymorphic support
  - [ ] Add endpoint to list available account types
  - [ ] Implement proper error handling and status codes
  - [ ] Update OpenAPI documentation for type schemas
  - [ ] Update response models to support polymorphic responses
  - [ ] Add feature flag service dependency
  - [ ] Filter available types based on feature flags
  - [ ] Add currency information to responses
  - [ ] Include international fields based on feature flags

- [ ] Update tests in `tests/integration/api/test_account_endpoints.py`:
  - [ ] Test authentication and authorization
  - [ ] Verify proper error status codes
  - [ ] Test polymorphic request validation
  - [ ] Test polymorphic response models
  - [ ] Test feature flag integration
  - [ ] Test multi-currency support
  - [ ] Test international banking fields

## Schema Factory Updates

- [ ] Update schema factories in `tests/helpers/schema_factories/accounts.py`:
  - [ ] Create/update base account factory functions
  - [ ] Set up structure for type-specific factories
  - [ ] Provide consistent interface for all factories
  - [ ] Use appropriate default values
  - [ ] Export factory functions in `__init__.py`
  - [ ] Add feature flag awareness to factories
  - [ ] Add currency support to factories
  - [ ] Add international banking field support

- [ ] Create tests in `tests/unit/helpers/test_account_schema_factories.py`:
  - [ ] Test factory function behavior
  - [ ] Verify default values
  - [ ] Test customization options
  - [ ] Test validation within factories
  - [ ] Test feature flag integration
  - [ ] Test currency customization
  - [ ] Test international field generation

## Documentation

- [ ] Update documentation:
  - [x] Document account type registry usage
  - [ ] Create examples for polymorphic operations
  - [x] Document schema validation patterns
  - [ ] Document repository query patterns
  - [ ] Document service layer integration
  - [ ] Document API changes
  - [x] Document feature flag integration
  - [x] Add multi-currency support documentation
  - [x] Document international banking support
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

- [ ] Base Account Schema Factory (`tests/helpers/schema_factories/accounts.py`):
  - [ ] Create/update base account factory functions
  - [ ] Support customization via **kwargs
  - [ ] Ensure proper defaults for required fields
  - [ ] Verify test helpers integrate with registry

- [ ] Banking Type Schema Factories:
  - [ ] `tests/helpers/schema_factories/account_types/banking/checking.py`:
    - [ ] Implement factory with appropriate defaults
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
  - [ ] `tests/integration/repositories/account_types/banking/test_payment_app.py`
  - [ ] `tests/integration/repositories/account_types/banking/test_bnpl.py`
  - [ ] `tests/integration/repositories/account_types/banking/test_ewa.py`

- [x] Repository Factory Tests (`tests/integration/repositories/test_factory.py`):
  - [x] Test dynamic module loading
  - [x] Test binding of specialized methods to base repository
  - [x] Verify feature flag integration in module loading
  - [x] Test fallback behavior when modules are missing

### Registry Testing

- [ ] Account Type Registry Tests (`tests/unit/registry/test_account_types.py`):
  - [ ] Test registration of account types
  - [ ] Verify retrieval of model and schema classes
  - [ ] Test filtering by category
  - [ ] Test get_repository_module() functionality
  - [ ] Verify feature flag integration for type availability

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

- [x] Apply feature flag integration (ADR-024):
  - [x] Integrate with FeatureFlagService
  - [x] Add conditional logic based on feature flags
  - [x] Handle graceful degradation for disabled features
  - [x] Test with feature flags enabled/disabled
  - [x] Document feature flag requirements

## Final Verification

Before completing ADR-016 implementation, verify:

1. **Architecture Compliance**:
   - [x] Polymorphic base structure is implemented correctly
   - [x] Registry mechanism works as designed
   - [x] Schema validation is consistent
   - [x] Repository layer handles polymorphic queries properly
   - [x] Feature flag integration works correctly
   - [x] Multi-currency support is implemented
   - [x] International banking fields are supported

2. **Test Coverage**:
   - [x] Base model has test coverage
   - [x] Registry has comprehensive tests
   - [x] Schema validation is thoroughly tested
   - [x] Repository methods have appropriate tests
   - [ ] Service methods have business rule tests
   - [ ] API endpoints have response tests
   - [x] Feature flag behavior is tested
   - [x] Currency support is tested
   - [x] International banking fields are tested

3. **Documentation**:
   - [x] Core architecture is well-documented
   - [ ] API changes are documented
   - [x] Schema validation rules are documented
   - [x] Registry usage is documented
   - [x] Feature flag integration is documented
   - [x] Multi-currency support is documented
   - [x] International banking support is documented

4. **Dependency Updates**:
   - [ ] Service layer uses registry properly
   - [ ] API layer integrates with polymorphic models
   - [x] Repository factories support new architecture
   - [x] Feature flag service is properly injected
   - [x] Currency utilities are available
   - [x] International banking validators are available
