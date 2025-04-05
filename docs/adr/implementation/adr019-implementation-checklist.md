# ADR-019 Implementation Checklist: Banking Account Types Expansion

This checklist outlines the specific tasks required to implement the Banking Account Types Expansion as defined in ADR-019. Each task includes verification criteria and integrated testing to ensure proper implementation at each stage.

## Current Status (April 5, 2025)

Overall completion: ~75%

Major completed components:

- Feature Flag Integration
- Database Schema and Model Implementation
- Pydantic Schema Implementation
- Repository Module Pattern Implementation
- Service Layer Implementation
- Business Logic Implementation
- Error Handling Implementation

Major remaining components:

- API Layer Implementation (4 key endpoints)
- Schema Factory Implementation
- Tests for Modern Financial Services Repositories
- Documentation Finalization

## Phase 1: Feature Flag Integration

### 1.1 Banking Account Types Feature Flag

- [x] Integrate with the feature flag system from ADR-024:
  - [x] Add dependency on feature flag service in relevant components
  - [x] Implement conditional logic for banking account types
  - [x] Add feature flag checks before exposing new account types
  - [x] Add proper error handling for disabled features

- [x] Add specific feature flag for banking account types:
  - [x] Use `BANKING_ACCOUNT_TYPES_ENABLED` flag from feature flag registry
  - [x] Configure default value (false in production)
  - [x] Document feature flag usage in code

**Verification:**

- ✅ Integration with feature flag system is working correctly
- ✅ New account types are only exposed when flag is enabled
- ✅ Error handling provides appropriate messages when features are disabled
- ✅ Documentation explains feature flag usage

**Testing:**

- [x] Test with feature flag enabled and disabled
- [x] Verify behavior changes correctly when flag is toggled
- [x] Test error handling when attempting to access disabled features
- [ ] Test feature flag persistence across application restarts

## Phase 2: Database Schema and Model Implementation

### 2.1 Base Account Model Enhancements

- [x] Update Account model to include currency field for international support
- [x] Add next_action_date and next_action_amount fields for performance optimization
- [x] Ensure all date fields use timezone-aware DateTime as per ADR-011
- [x] Verify Account model includes is_closed field with default=False
- [x] Add appropriate indexes to the Account model (account_type, user_id, is_closed)
- [x] Add composite index on (user_id, account_type) for frequent queries

**Verification:**

- ✅ SQLAlchemy model reflects all required fields
- ✅ Indexes are properly defined in the model
- ✅ Model passes linting and type checking

**Testing:**

- [x] Write unit tests for base Account model validating field definitions
- [x] Test index creation and effectiveness with sample queries
- [x] Verify datetime fields store timezone-aware values correctly
- [x] Test feature flag integration with model access

### 2.2 Traditional Banking Account Models

- [x] Implement CheckingAccount model with all fields defined in ADR-019
  - Include routing_number, has_overdraft_protection, overdraft_limit, monthly_fee, interest_rate
  - Add international fields: iban, swift_bic, sort_code, branch_code, account_format
- [x] Implement SavingsAccount model with all required fields
  - interest_rate, compound_frequency, interest_earned_ytd, withdrawal_limit, minimum_balance
- [x] Implement CreditAccount model with all required fields
  - credit_limit, statement_balance, statement_due_date, minimum_payment, apr, annual_fee, rewards_program, autopay_status, last_statement_date
- [x] Ensure all models inherit properly from Account base model
- [x] Verify polymorphic_identity is correctly set for each model
- [x] Configure appropriate nullable constraints on required fields

**Verification:**

- ✅ All model fields match ADR-019 specifications
- ✅ Foreign key relationships are properly configured
- ✅ Models follow SQLAlchemy best practices
- ✅ Appropriate CHECK constraints are defined where needed

**Testing:**

- [x] Write unit tests for each account model verifying inheritance works properly
- [x] Test foreign key constraints and cascading behavior
- [x] Test field constraints (e.g., nullable, defaults) with valid and invalid data
- [x] Write integration tests for polymorphic queries on each model type

### 2.3 Modern Financial Services Models

- [x] Implement PaymentAppAccount model with defined fields
  - platform, has_debit_card, card_last_four, linked_account_ids, supports_direct_deposit, supports_crypto
- [x] Implement BNPLAccount model with all required fields
  - original_amount, installment_count, installments_paid, installment_amount, payment_frequency, next_payment_date, promotion_info, late_fee, bnpl_provider
- [x] Implement EWAAccount model with defined fields
  - provider, max_advance_percentage, per_transaction_fee, pay_period_start, pay_period_end, next_payday
- [x] Ensure all models inherit properly from Account base model
- [x] Verify polymorphic_identity is correctly set for each model
- [x] Configure appropriate nullable constraints on required fields

**Verification:**

- ✅ All model fields match ADR-019 specifications
- ✅ Foreign key relationships are properly configured
- ✅ Models follow SQLAlchemy best practices
- ✅ Field constraints match business rules

**Testing:**

- [x] Write unit tests for each modern account model
- [x] Test special business logic for BNPL lifecycle management
- [ ] Test relationships between PaymentApp and linked accounts
- [x] Write integration tests for polymorphic queries
- [x] Test validation constraints at the database level

## Phase 3: Pydantic Schema Implementation

### 3.1 Base Schema Enhancements

- [x] Update AccountBase, AccountCreate, and AccountResponse schemas as needed
- [x] Ensure proper MoneyDecimal and PercentageDecimal usage as per ADR-013
- [x] Verify field validators follow Pydantic V2 patterns with @field_validator
- [x] Add appropriate validators for currency and international fields
- [x] Implement proper date validation for all datetime fields
- [x] Add documentation alongside schema implementation

**Verification:**

- ✅ Schemas correctly use MoneyDecimal and PercentageDecimal types
- ✅ Validators follow Pydantic V2 pattern with @classmethod and @field_validator
- ✅ All required fields are present
- ✅ Class Config uses orm_mode=True for response schemas
- ✅ Schemas follow ADR-012 validation layer standards

**Testing:**

- [x] Write unit tests for base schemas with valid and invalid data
- [x] Test datetime field validation for timezone awareness
- [x] Test currency field validation with various currency codes
- [x] Test schema validation error messages for clarity
- [x] Verify feature flag integration with schema validation

### 3.2 Traditional Banking Account Schemas

- [x] Implement CheckingAccountCreate and CheckingAccountResponse schemas
  - Include validators for routing_number format
  - Add validator for overdraft_limit when has_overdraft_protection is True
  - Add validators for international banking fields
- [x] Implement SavingsAccountCreate and SavingsAccountResponse schemas
  - Include validators for interest_rate (must be valid percentage)
  - Add validator for compound_frequency (must be valid option)
- [x] Implement CreditAccountCreate and CreditAccountResponse schemas
  - Include validators for credit_limit (must be positive)
  - Add validators for statement_balance, minimum_payment
  - Add validator for autopay_status (must be valid option)
- [x] Create documentation alongside schema implementation

**Verification:**

- ✅ All schemas include appropriate Literal["account_type"] field
- ✅ Validators properly enforce business rules
- ✅ Error messages are clear and actionable
- ✅ Response schemas include all fields from models
- ✅ Create schemas include appropriate defaults

**Testing:**

- [x] Write unit tests for each schema's validators
- [x] Test all validation rules with valid and invalid data
- [x] Test error messages for clarity and accuracy
- [x] Test inheritance behavior from base schemas
- [x] Verify field constraints match business requirements

### 3.3 Modern Financial Services Schemas

- [x] Implement PaymentAppAccountCreate and PaymentAppAccountResponse schemas
  - Include validator for platform (must be in list of valid platforms)
  - Add validator for card_last_four format when has_debit_card is True
- [x] Implement BNPLAccountCreate and BNPLAccountResponse schemas
  - Include validators for installment_count (must be positive)
  - Add validator for payment_frequency (must be valid option)
  - Add validator for next_payment_date (must be in future for new accounts)
- [x] Implement EWAAccountCreate and EWAAccountResponse schemas
  - Include validator for max_advance_percentage (must be 0-100%)
  - Add validator for next_payday (must be in future for new accounts)
- [x] Create documentation alongside schema implementation

**Verification:**

- ✅ All schemas include appropriate Literal["account_type"] field
- ✅ Validators properly enforce business rules
- ✅ Error messages are clear and actionable
- ✅ Response schemas include all fields from models
- ✅ Create schemas include appropriate defaults

**Testing:**

- [x] Write unit tests for each schema focusing on unique validations
- [x] Test BNPL-specific validations for installments and payments
- [x] Test PaymentApp platform validation with valid and invalid values
- [x] Test date validations for EWA payday requirements
- [x] Test internationalization aspects of schemas

### 3.4 Discriminated Union Implementation

- [x] Implement BankingAccountCreateUnion using Pydantic's Annotated and Union
- [x] Implement BankingAccountResponseUnion using Pydantic's Annotated and Union
- [x] Ensure all account types are included in the unions
- [x] Set up proper discriminator configuration
- [x] Create documentation for union type usage

**Verification:**

- ✅ Union types include all account subtypes
- ✅ Field(discriminator="account_type") is configured
- ✅ Union types work correctly with FastAPI
- ✅ Serialization and deserialization work as expected

**Testing:**

- [x] Test serialization and deserialization of each account type via the union
- [x] Test discriminator behavior with various account types
- [ ] Test API integration with the union types
- [ ] Test with feature flags to verify behavior when types are disabled
- [ ] Write integration tests for end-to-end schema validation

## Phase 4: Repository Layer Implementation

### 4.1 Repository Module Pattern Implementation

- [x] Implement Repository Module Pattern:
  - [x] Create modular directory structure for account types
  - [x] Create base AccountRepository with common operations
  - [x] Implement dynamic repository factory with module loading
  - [x] Add feature flag integration in repository layer
  - [x] Create README with pattern documentation

**Verification:**

- ✅ Modular structure follows established patterns
- ✅ Repository factory dynamically loads modules
- ✅ Feature flags control available functionality
- ✅ Documentation clearly explains the pattern

**Testing:**

- [x] Write unit tests for repository factory
- [x] Test dynamic module loading
- [x] Test with real database and real data
- [x] Verify proper error handling with edge cases
- [x] Test with feature flags enabled and disabled

### 4.2 Type-Specific Repository Modules

- [x] Implement banking type repositories as modules:
  - [x] Create checking.py with checking-specific operations
  - [x] Create savings.py with savings-specific operations
  - [x] Create credit.py with credit-specific operations
  - [x] Set up module exports in __init__.py files
  - [x] Add feature flag checks in appropriate methods

**Verification:**

- ✅ Each module contains type-specific operations
- ✅ Methods use appropriate SQLAlchemy querying techniques
- ✅ Methods return strongly typed results
- ✅ Feature flags control availability of operations
- ✅ Modules are structured for scalability

**Testing:**

- [x] Write unit tests for each type-specific repository module
- [x] Test with various account statuses (open, closed)
- [x] Test with realistic data including multiple account types
- [x] Verify order and filtering work correctly
- [x] Test performance with larger datasets
- [x] Test edge cases like no accounts found

### 4.3 Integration with Bill Split Repository

- [x] Update BillSplitRepository to work with polymorphic account types
- [x] Add validation for eligible account types for bill splits
- [x] Implement methods to retrieve bill splits by account type
- [x] Ensure proper transaction handling for bill splits
- [x] Create documentation for bill split integration

**Verification:**

- ✅ BillSplitRepository works correctly with all account types
- ✅ Foreign key relationships are handled properly
- ✅ Queries join correctly to polymorphic account tables
- ✅ Transaction boundaries are properly defined
- ✅ Method signatures follow repository pattern

**Testing:**

- [x] Test bill splits with each eligible account type
- [x] Test validation rules for ineligible account types
- [x] Test transaction handling across multiple entities
- [x] Verify polymorphic queries return correct bill splits
- [x] Test with feature flags to ensure proper integration

## Phase 5: Service Layer Implementation

### 5.1 Account Service Enhancements

- [x] Extend AccountService with banking-specific methods
- [x] Implement get_upcoming_payments method
- [x] Implement get_banking_overview method
- [x] Implement update_bnpl_status method
- [x] Add comprehensive error handling with specific error classes
- [x] Integrate with feature flag system
- [x] Create documentation alongside service implementation

**Verification:**

- ✅ Service injects repository dependencies
- ✅ Methods validate input parameters
- ✅ Business rules are properly implemented
- ✅ Error handling uses appropriate error classes
- ✅ Methods return appropriate types
- ✅ No direct ORM operations in service methods

**Testing:**

- [x] Write unit tests for all service methods
- [x] Test business rule validation
- [x] Test with feature flags enabled and disabled
- [x] Test error handling for various scenarios
- [x] Test aggregation and calculation logic
- [x] Test lifecycle management of temporary accounts (BNPL)

### 5.2 Business Logic Implementation

- [x] Implement balance calculation logic for different account types
- [x] Implement due date tracking across account types
- [x] Implement account lifecycle management (especially for BNPL)
- [x] Implement validation rules for account operations
- [x] Create documentation for business logic

**Verification:**

- ✅ Balance semantics are handled correctly for each account type
- ✅ Due date calculations follow ADR-011 datetime standards
- ✅ Lifecycle transitions are properly managed
- ✅ Validation rules match business requirements
- ✅ Methods return appropriate error messages

**Testing:**

- [x] Test balance calculations for assets vs. liabilities
- [x] Test due date tracking with datetime manipulation
- [x] Test BNPL lifecycle from creation through completion
- [x] Test validation rules with valid and invalid data
- [x] Write integration tests for end-to-end business flows
- [x] Test edge cases like account status changes

### 5.3 Error Handling Implementation

- [x] Implement hierarchical error structure as defined in ADR-019
- [x] Create specific error classes for validation failures
- [x] Implement type-specific error classes
- [x] Ensure error messages are clear and actionable
- [x] Document error handling strategy and usage

**Verification:**

- ✅ Error hierarchy matches ADR-019 specification
- ✅ Error classes include appropriate codes and HTTP status codes
- ✅ Error messages are user-friendly
- ✅ Type-specific errors provide detailed information
- ✅ Errors are properly propagated through the service layer

**Testing:**

- [x] Write unit tests for each error class
- [x] Test error propagation through service layers
- [x] Test error message clarity and actionability
- [x] Test error handling in edge cases
- [x] Verify error responses match expected format
- [x] Test internationalization of error messages

## Phase 6: API Layer Implementation

### 6.1 Banking API Endpoints

- [ ] Implement GET /banking/overview endpoint
- [ ] Implement GET /banking/upcoming-payments endpoint
- [ ] Implement POST /accounts/banking endpoint
- [ ] Implement POST /accounts/bnpl/{account_id}/update-status endpoint
- [ ] Ensure proper response models and status codes
- [ ] Integrate with feature flag system
- [ ] Create OpenAPI documentation alongside endpoints

**Verification:**

- ❓ Endpoints need to be implemented
- ❓ Response models need to match repository/service returns
- ❓ Input validation needs to use Pydantic schemas
- ❓ Endpoints need to include appropriate OpenAPI documentation
- ❓ Authentication and authorization need to be properly enforced

**Testing:**

- [ ] Write integration tests for each API endpoint
- [ ] Test authentication and authorization scenarios
- [ ] Test with valid and invalid input data
- [ ] Test with feature flags enabled and disabled
- [ ] Verify error responses match expected format
- [ ] Load test endpoints with realistic traffic volumes

### 6.2 Account Type Registry Integration

- [x] Update AccountTypeRegistry initialization with new account types
- [x] Register all banking account types with appropriate metadata
- [ ] Implement API endpoint to retrieve available account types
- [ ] Implement API endpoint to retrieve account types by category

**Verification:**

- ✅ Registry includes all account types defined in ADR-019
- ✅ Registration includes model_class, schema_class, name, description, category
- ❓ API endpoints need to be implemented to return account type information
- ✅ Registry handles unknown types gracefully

**Testing:**

- [x] Test registry initialization with all account types
- [x] Test type retrieval by ID and category
- [ ] Test API endpoints for returning account types
- [x] Test feature flag integration with registry

### 6.3 Error Response Formatting

- [ ] Implement consistent error response format
- [ ] Map specific error classes to HTTP status codes
- [ ] Ensure error details include field-level information where appropriate
- [ ] Test error responses for various failure scenarios

**Verification:**

- ❓ Error response format needs to be implemented
- ❓ HTTP status codes need to match error types
- ❓ Error messages need to be clear and actionable
- ❓ Validation errors need to include field-specific details
- ❓ Error handling shouldn't expose sensitive information

**Testing:**

- [ ] Test error responses for all API endpoints
- [ ] Test error response format for various error types
- [ ] Test field-level error information in validation failures
- [ ] Test error responses with feature flags enabled/disabled

## Phase 7: Performance Optimization

### 7.1 Database Optimization

- [x] Implement comprehensive indexing strategy
- [x] Add denormalization fields for frequent queries
- [ ] Implement query caching for frequently accessed data
- [ ] Configure appropriate connection pooling
- [ ] Document optimization strategies

**Verification:**

- ✅ Indexes are created for common query patterns
- ✅ Denormalization fields are implemented (next_action_date/amount)
- ❓ Cache invalidation needs to be implemented
- ❓ Connection pooling needs to be configured

**Testing:**

- [x] Benchmark common queries with and without indexes
- [ ] Test cache hit/miss scenarios
- [x] Verify index usage with query plans
- [ ] Load test with concurrent connections
- [x] Test with larger datasets to verify scaling

## Next Steps (Prioritized)

1. **Implement API Endpoints**
   - Implement GET /banking/overview endpoint
   - Implement GET /banking/upcoming-payments endpoint
   - Implement POST /accounts/banking endpoint
   - Implement POST /accounts/bnpl/{account_id}/update-status endpoint
   - Create comprehensive tests for each endpoint

2. **Complete Schema Factory Implementation**
   - Create schema factories for all banking account types
   - Implement proper defaults and customization options
   - Add tests for schema factories
   - Update tests to use schema factories where appropriate

3. **Complete Modern Financial Services Repository Tests**
   - Implement tests for PaymentApp repository
   - Implement tests for BNPL repository
   - Implement tests for EWA repository
   - Test linked account operations and relationships

4. **Finalize Documentation**
   - Complete docstrings for all public methods
   - Update OpenAPI schema with new endpoints
   - Document error handling strategy and response format
   - Create examples for API usage

## Testing Strategy (April 3, 2025)

Following Debtonator's "Real Objects Testing Philosophy," we'll implement a structured, progressive testing approach for Banking Account Types. This strategy ensures thorough validation of each layer before moving to the next, mirrors the codebase structure, and requires no mocks or monkeypatching.

### Testing Sequence and Structure
- Testing progression: models → schemas → schema factories → repositories → service → API
- Mirror the exact source code directory structure in test files
- Create modular test files to keep tests focused and maintainable
- Schema factories must be created and tested before repository tests

### Models Testing

- [x] Banking Account Type Models Tests:
  - [x] `tests/unit/models/account_types/banking/test_checking.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "checking"
    - [x] Validate international fields (iban, swift_bic, sort_code, etc.)
    - [x] Test overdraft-related fields
  - [x] `tests/unit/models/account_types/banking/test_savings.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "savings"
    - [x] Test interest rate fields
    - [x] Validate withdrawal_limit and minimum_balance
  - [x] `tests/unit/models/account_types/banking/test_credit.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "credit"
    - [x] Test credit limit and statement fields
    - [x] Validate autopay_status options
  - [x] `tests/unit/models/account_types/banking/test_payment_app.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "payment_app"
    - [x] Test platform field constraints
    - [x] Validate debit card related fields
  - [x] `tests/unit/models/account_types/banking/test_bnpl.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "bnpl"
    - [x] Test installment fields
    - [x] Validate payment_frequency options
  - [x] `tests/unit/models/account_types/banking/test_ewa.py`:
    - [x] Test table definition and columns
    - [x] Verify inheritance from Account base model
    - [x] Test polymorphic identity is "ewa"
    - [x] Test pay period fields
    - [x] Validate advance percentage limits

### Schemas Testing

- [x] Banking Account Type Schema Tests:
  - [x] `tests/unit/schemas/account_types/banking/test_checking.py`:
    - [x] Test Literal["checking"] type enforcement
    - [x] Test overdraft validation (limit required when protection enabled)
    - [x] Test international banking field validations
    - [x] Test create and response schema differences
  - [x] `tests/unit/schemas/account_types/banking/test_savings.py`:
    - [x] Test Literal["savings"] type enforcement
    - [x] Test interest_rate validation (must be valid percentage)
    - [x] Test compound_frequency validation (must be valid option)
    - [x] Test minimum_balance and withdrawal_limit validation
  - [x] `tests/unit/schemas/account_types/banking/test_credit.py`:
    - [x] Test Literal["credit"] type enforcement
    - [x] Test credit_limit validation (must be positive)
    - [x] Test statement_balance/minimum_payment relationship validation
    - [x] Test autopay_status validation
  - [x] `tests/unit/schemas/account_types/banking/test_payment_app.py`:
    - [x] Test Literal["payment_app"] type enforcement
    - [x] Test platform validation (must be in approved list)
    - [x] Test card_last_four validation when has_debit_card is True
    - [x] Test linked_account_ids parsing
  - [x] `tests/unit/schemas/account_types/banking/test_bnpl.py`:
    - [x] Test Literal["bnpl"] type enforcement
    - [x] Test installment_count/installments_paid validation
    - [x] Test payment_frequency validation
    - [x] Test next_payment_date validation (must be future for new)
  - [x] `tests/unit/schemas/account_types/banking/test_ewa.py`:
    - [x] Test Literal["ewa"] type enforcement
    - [x] Test max_advance_percentage validation (0-100%)
    - [x] Test pay period field validations
    - [x] Test next_payday validation (must be future)

- [ ] Banking Union Schema Tests:
  - [ ] `tests/unit/schemas/account_types/banking/test_unions.py`:
    - [ ] Test BankingAccountCreateUnion discriminated union
    - [ ] Test BankingAccountResponseUnion discriminated union
    - [ ] Verify proper deserialization based on account_type
    - [ ] Test error handling for invalid account types
    - [ ] Test with feature flags enabled/disabled

### Schema Factories

- [ ] Banking Type Schema Factories:
  - [ ] `tests/helpers/schema_factories/account_types/banking/checking.py`:
    - [ ] Implement create_checking_account_schema with appropriate defaults
    - [ ] Support customization via **kwargs for all fields
    - [ ] Handle international banking fields
  - [ ] `tests/helpers/schema_factories/account_types/banking/savings.py`:
    - [ ] Implement create_savings_account_schema with appropriate defaults
    - [ ] Support interest rate customization
  - [ ] `tests/helpers/schema_factories/account_types/banking/credit.py`:
    - [ ] Implement create_credit_account_schema with appropriate defaults
    - [ ] Support statement-related field customization
  - [ ] `tests/helpers/schema_factories/account_types/banking/payment_app.py`:
    - [ ] Implement create_payment_app_account_schema with appropriate defaults
    - [ ] Support platform customization
  - [ ] `tests/helpers/schema_factories/account_types/banking/bnpl.py`:
    - [ ] Implement create_bnpl_account_schema with appropriate defaults
    - [ ] Support installment field customization
  - [ ] `tests/helpers/schema_factories/account_types/banking/ewa.py`:
    - [ ] Implement create_ewa_account_schema with appropriate defaults
    - [ ] Support pay period customization

- [ ] Schema Factory Tests:
  - [ ] `tests/unit/helpers/schema_factories/account_types/banking/test_checking.py`:
    - [ ] Test default schema generation with valid values
    - [ ] Test customization via kwargs
    - [ ] Verify schema validates successfully
  - [ ] Similar tests for other account types

### Repository Testing

- [x] Repository Module Tests:
  - [x] `tests/integration/repositories/account_types/banking/test_checking.py`:
    - [x] Test checking-specific repository functions
    - [x] Test querying with international banking fields
    - [x] Test overdraft-related operations
  - [x] `tests/integration/repositories/account_types/banking/test_savings.py`:
    - [x] Test savings-specific repository functions
    - [x] Test interest-related operations
  - [x] `tests/integration/repositories/account_types/banking/test_credit.py`:
    - [x] Test credit-specific repository functions
    - [x] Test statement-related operations
    - [x] Test due date querying
  - [ ] `tests/integration/repositories/account_types/banking/test_payment_app.py`:
    - [ ] Test payment app-specific repository functions
    - [ ] Test linked account operations
  - [ ] `tests/integration/repositories/account_types/banking/test_bnpl.py`:
    - [ ] Test BNPL-specific repository functions
    - [ ] Test installment tracking
    - [ ] Test next payment calculations
  - [ ] `tests/integration/repositories/account_types/banking/test_ewa.py`:
    - [ ] Test EWA-specific repository functions
    - [ ] Test pay period operations

- [x] Cross-Account Operations Tests:
  - [x] `tests/integration/repositories/account_types/banking/test_banking_operations.py`:
    - [x] Test operations across multiple banking account types
    - [x] Test polymorphic queries with banking types
    - [x] Test feature flag controlled operations

### Service Layer Testing

- [x] Banking Service Tests:
  - [x] `tests/integration/services/test_banking_overview.py`:
    - [x] Test get_banking_overview aggregation
    - [x] Test with multiple account types
    - [x] Verify calculation accuracy
  - [x] `tests/integration/services/test_upcoming_payments.py`:
    - [x] Test get_upcoming_payments across account types
    - [x] Test sorting and filtering
    - [x] Verify date handling
  - [x] `tests/integration/services/test_bnpl_lifecycle.py`:
    - [x] Test update_bnpl_status lifecycle management
    - [x] Test payment status transitions
    - [x] Test account closure upon final payment

### API Testing

- [ ] Banking API Tests:
  - [ ] `tests/integration/api/v1/banking/test_overview.py`:
    - [ ] Test GET /banking/overview endpoint
    - [ ] Test with various account combinations
    - [ ] Test with feature flags enabled/disabled
  - [ ] `tests/integration/api/v1/banking/test_upcoming_payments.py`:
    - [ ] Test GET /banking/upcoming-payments endpoint
    - [ ] Test with different date parameters
    - [ ] Test sorting and filtering
  - [ ] `tests/integration/api/v1/banking/test_accounts.py`:
    - [ ] Test POST /accounts/banking endpoint
    - [ ] Test with different account types
    - [ ] Test validation
