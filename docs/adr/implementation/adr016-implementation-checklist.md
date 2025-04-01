# ADR-016 Account Type Expansion - Core Architecture Implementation Checklist

This checklist focuses specifically on implementing the core polymorphic architecture described in ADR-016, which establishes the foundation for the account type expansion project. The subsequent specialized account types will be implemented through separate ADRs (ADR-019 through ADR-023).

## Base Account Model

- [ ] Refactor existing Account model to use polymorphic inheritance:
  - [ ] Rename `type` field to `account_type` for clarity (discriminator column)
  - [ ] Update all existing code to use `account_type` instead of `type`
  - [ ] Configure SQLAlchemy polymorphic identity mapping
  - [ ] Add `is_closed` flag for account lifecycle management
  - [ ] Use `Numeric(12, 4)` for all monetary fields per ADR-013
  - [ ] Add proper UTC-aware datetime fields per ADR-011
  - [ ] Add appropriate indexes, particularly on `account_type`
  - [ ] Add `currency` field with ISO 4217 currency code (for multi-currency support)
  - [ ] Set default currency to "USD" for backward compatibility

- [ ] Update Account model tests:
  - [ ] Verify polymorphic identity mapping
  - [ ] Test proper relationship declarations
  - [ ] Ensure datetime fields comply with ADR-011
  - [ ] Test balance field decimal precision per ADR-013
  - [ ] Test currency field validation
  - [ ] Test default currency behavior

## Multi-Currency Support

- [ ] Implement multi-currency support in base models:
  - [ ] Add `currency` field to Account model (ISO 4217 code)
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

- [ ] Implement internationalization fields in CheckingAccount model:
  - [ ] Add `iban` field for International Bank Account Number
  - [ ] Add `swift_bic` field for SWIFT/BIC codes
  - [ ] Add `sort_code` field for UK and Ireland
  - [ ] Add `branch_code` field for various countries
  - [ ] Add `account_format` field to indicate format in use

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

- [ ] Create feature flag tests:
  - [ ] Test behavior with flags enabled
  - [ ] Test behavior with flags disabled
  - [ ] Test transitions between states
  - [ ] Test error handling for disabled features

## Account Type Registry

- [ ] Create `src/registry/account_types.py`:
  - [ ] Implement `AccountTypeRegistry` class with empty dictionary
  - [ ] Add `register()` method for type registration
  - [ ] Create `get_model_class()` method to retrieve model classes
  - [ ] Create `get_schema_class()` method to retrieve schema classes
  - [ ] Add methods to get all types or filter by category
  - [ ] Implement methods to get types by ID or name
  - [ ] Set up singleton pattern for registry access
  - [ ] Add integration with feature flag system to filter available types

- [ ] Create `tests/unit/registry/test_account_type_registry.py`:
  - [ ] Test registration of account types
  - [ ] Test retrieval of model and schema classes
  - [ ] Test filtering by category
  - [ ] Test registry initialization with base types
  - [ ] Test error handling for unknown types
  - [ ] Test feature flag integration for type availability

## Base Schema Architecture

- [ ] Create/update schema base classes in `src/schemas/accounts.py`:
  - [ ] Update `AccountBase` with common fields
  - [ ] Create/update `AccountCreate` with account_type discriminator
  - [ ] Create/update `AccountResponse` with common output fields
  - [ ] Add validator for account_type field
  - [ ] Use MoneyDecimal for monetary fields per ADR-013
  - [ ] Set up Pydantic's discriminated union for polymorphic schemas
  - [ ] Add currency field and validation
  - [ ] Add conditional field inclusion based on feature flags

- [ ] Create/update schema tests in `tests/unit/schemas/test_account_schemas.py`:
  - [ ] Test field constraints and validation
  - [ ] Test discriminated union behavior
  - [ ] Test error cases with invalid data
  - [ ] Test MoneyDecimal validation for 2 decimal precision
  - [ ] Test validation of required vs. optional fields
  - [ ] Test currency validation
  - [ ] Test feature flag integration for field inclusion

## Repository Layer

- [ ] Enhance `src/repositories/accounts.py`:
  - [ ] Update `AccountRepository` to handle polymorphic queries
  - [ ] Implement `get_with_type()` for loading specific subtypes
  - [ ] Add `get_by_type()` for filtering by account type
  - [ ] Create `get_by_user_and_type()` for user-specific queries
  - [ ] Implement type-specific create and update methods
  - [ ] Add methods to list available account types
  - [ ] Ensure proper transaction handling for polymorphic operations
  - [ ] Add feature flag service dependency
  - [ ] Filter available types based on feature flags
  - [ ] Add currency-aware query methods
  - [ ] Handle international fields based on feature flags

- [ ] Create/update tests in `tests/integration/repositories/test_account_repository.py`:
  - [ ] Follow the Arrange-Schema-Act-Assert pattern
  - [ ] Test polymorphic queries and joins
  - [ ] Test type-specific operations
  - [ ] Test proper relationship loading
  - [ ] Test error handling for polymorphic operations
  - [ ] Test feature flag integration
  - [ ] Test behavior with flags enabled/disabled
  - [ ] Test currency-specific operations
  - [ ] Test international field handling

## Service Layer

- [ ] Enhance `src/services/accounts.py`:
  - [ ] Update `AccountService` to work with the `AccountTypeRegistry`
  - [ ] Implement type-specific validation in service layer
  - [ ] Add business rule application for different account types
  - [ ] Create user-friendly error messages for validation failures
  - [ ] Handle proper type-specific create and update operations
  - [ ] Implement methods to get available account types
  - [ ] Add feature flag service dependency
  - [ ] Add conditional logic based on feature flags
  - [ ] Implement currency-aware business logic
  - [ ] Add international banking field validation

- [ ] Update tests in `tests/unit/services/test_account_service.py`:
  - [ ] Test with real repositories (no mocks)
  - [ ] Verify business rule validation
  - [ ] Test type-specific behavior
  - [ ] Test error handling for invalid cases
  - [ ] Test feature flag integration
  - [ ] Test multi-currency operations
  - [ ] Test international banking validation

## Integration with Bill Splits

- [ ] Update Bill Split model to work with polymorphic accounts:
  - [ ] Ensure BillSplit references base Account model
  - [ ] Update bill split repository to handle polymorphic accounts
  - [ ] Add validation for account type compatibility with bill splits
  - [ ] Add currency handling for bill splits
  - [ ] Add feature flag checks for bill split operations

- [ ] Update tests in `tests/integration/repositories/test_bill_split_repository.py`:
  - [ ] Test bill splits assigned to different account types
  - [ ] Test validation rules for compatible account types
  - [ ] Verify proper relationship loading
  - [ ] Test transaction boundaries with complex operations
  - [ ] Test multi-currency bill splits
  - [ ] Test feature flag integration

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
  - [ ] Document account type registry usage
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

- [ ] Update initialization code:
  - [ ] Set up registry initialization
  - [ ] Register base account types
  - [ ] Configure database initialization
  - [ ] Set up test fixtures
  - [ ] Add feature flag initialization
  - [ ] Configure currency support
  - [ ] Initialize international banking support

## Testing Strategy

Follow Debtonator's "Real Objects Testing Philosophy" for all tests:

1. **No Mocks Policy**:
   - [ ] Ensure no usage of unittest.mock or MagicMock
   - [ ] Use real objects, real repositories, and real schemas
   - [ ] Set up real test database fixtures for polymorphic testing

2. **Integration-First Approach**:
   - [ ] Verify actual cross-layer interactions
   - [ ] Test repositories with real database sessions
   - [ ] Test services with real repositories
   - [ ] Test feature flag integration across layers
   - [ ] Test multi-currency support in real scenarios
   - [ ] Test international banking fields in real database

3. **Comprehensive Coverage**:
   - [ ] Test polymorphic base functionality
   - [ ] Test registry operations
   - [ ] Test repository polymorphic methods
   - [ ] Test service validation and business rules
   - [ ] Test API endpoints and responses
   - [ ] Test feature flag enabled/disabled states
   - [ ] Test currency validation and operations
   - [ ] Test international banking validation

## Code Review Checklist Compliance

- [ ] Apply schema validation standards (ADR-012):
  - [ ] Ensure schemas extend BaseSchemaValidator
  - [ ] Use Field annotations for constraints
  - [ ] Implement cross-field validation
  - [ ] Provide clear field documentation
  - [ ] Add currency validation
  - [ ] Add international banking field validation

- [ ] Apply decimal precision standards (ADR-013):
  - [ ] Use MoneyDecimal for monetary values
  - [ ] Use Numeric(12, 4) for database columns
  - [ ] Implement proper rounding at UI boundaries
  - [ ] Ensure consistent handling across currencies

- [ ] Apply datetime standards (ADR-011):
  - [ ] Ensure all datetime fields use UTC
  - [ ] Use datetime_utils functions consistently
  - [ ] Validate datetime fields for timezone awareness

- [ ] Apply repository pattern standards (ADR-014):
  - [ ] Extend BaseRepository properly
  - [ ] Implement proper transaction management
  - [ ] Use proper relationship loading strategies
  - [ ] Add feature flag integration
  - [ ] Handle currency-specific operations
  - [ ] Support international banking fields

- [ ] Apply feature flag integration (ADR-024):
  - [ ] Integrate with FeatureFlagService
  - [ ] Add conditional logic based on feature flags
  - [ ] Handle graceful degradation for disabled features
  - [ ] Test with feature flags enabled/disabled
  - [ ] Document feature flag requirements

## Final Verification

Before completing ADR-016 implementation, verify:

1. **Architecture Compliance**:
   - [ ] Polymorphic base structure is implemented correctly
   - [ ] Registry mechanism works as designed
   - [ ] Schema validation is consistent
   - [ ] Repository layer handles polymorphic queries properly
   - [ ] Feature flag integration works correctly
   - [ ] Multi-currency support is implemented
   - [ ] International banking fields are supported

2. **Test Coverage**:
   - [ ] Base model has test coverage
   - [ ] Registry has comprehensive tests
   - [ ] Schema validation is thoroughly tested
   - [ ] Repository methods have appropriate tests
   - [ ] Service methods have business rule tests
   - [ ] API endpoints have response tests
   - [ ] Feature flag behavior is tested
   - [ ] Currency support is tested
   - [ ] International banking fields are tested

3. **Documentation**:
   - [ ] Core architecture is well-documented
   - [ ] API changes are documented
   - [ ] Schema validation rules are documented
   - [ ] Registry usage is documented
   - [ ] Feature flag integration is documented
   - [ ] Multi-currency support is documented
   - [ ] International banking support is documented

4. **Dependency Updates**:
   - [ ] Service layer uses registry properly
   - [ ] API layer integrates with polymorphic models
   - [ ] Repository factories support new architecture
   - [ ] Feature flag service is properly injected
   - [ ] Currency utilities are available
   - [ ] International banking validators are available
