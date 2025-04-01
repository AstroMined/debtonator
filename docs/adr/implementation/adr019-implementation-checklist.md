# ADR-019 Implementation Checklist: Banking Account Types Expansion

This checklist outlines the specific tasks required to implement the Banking Account Types Expansion as defined in ADR-019. Each task includes verification criteria and integrated testing to ensure proper implementation at each stage.

## Phase 1: Feature Flag Integration

### 1.1 Banking Account Types Feature Flag

- [ ] Integrate with the feature flag system from ADR-024:
  - [ ] Add dependency on feature flag service in relevant components
  - [ ] Implement conditional logic for banking account types
  - [ ] Add feature flag checks before exposing new account types
  - [ ] Add proper error handling for disabled features

- [ ] Add specific feature flag for banking account types:
  - [ ] Use `BANKING_ACCOUNT_TYPES_ENABLED` flag from feature flag registry
  - [ ] Configure default value (false in production)
  - [ ] Document feature flag usage in code

**Verification:**
- Integration with feature flag system is working correctly
- New account types are only exposed when flag is enabled
- Error handling provides appropriate messages when features are disabled
- Documentation explains feature flag usage

**Testing:**
- [ ] Test with feature flag enabled and disabled
- [ ] Verify behavior changes correctly when flag is toggled
- [ ] Test error handling when attempting to access disabled features
- [ ] Test feature flag persistence across application restarts

## Phase 2: Database Schema and Model Implementation

### 2.1 Base Account Model Enhancements

- [ ] Update Account model to include currency field for international support
- [ ] Add next_action_date and next_action_amount fields for performance optimization
- [ ] Ensure all date fields use timezone-aware DateTime as per ADR-011
- [ ] Verify Account model includes is_closed field with default=False
- [ ] Add appropriate indexes to the Account model (account_type, user_id, is_closed)
- [ ] Add composite index on (user_id, account_type) for frequent queries

**Verification:**
- Database migration script creates appropriate columns
- SQLAlchemy model reflects all required fields
- Indexes are properly defined in the model
- Model passes linting and type checking

**Testing:**
- [ ] Write unit tests for base Account model validating field definitions
- [ ] Test index creation and effectiveness with sample queries
- [ ] Verify datetime fields store timezone-aware values correctly
- [ ] Test feature flag integration with model access

### 2.2 Traditional Banking Account Models

- [ ] Implement CheckingAccount model with all fields defined in ADR-019
  - Include routing_number, has_overdraft_protection, overdraft_limit, monthly_fee, interest_rate
  - Add international fields: iban, swift_bic, sort_code, branch_code, account_format
- [ ] Implement SavingsAccount model with all required fields
  - interest_rate, compound_frequency, interest_earned_ytd, withdrawal_limit, minimum_balance
- [ ] Implement CreditAccount model with all required fields
  - credit_limit, statement_balance, statement_due_date, minimum_payment, apr, annual_fee, rewards_program, autopay_status, last_statement_date
- [ ] Ensure all models inherit properly from Account base model
- [ ] Verify polymorphic_identity is correctly set for each model
- [ ] Configure appropriate nullable constraints on required fields

**Verification:**
- All model fields match ADR-019 specifications
- Database migration script creates all required tables and columns
- Foreign key relationships are properly configured
- Models follow SQLAlchemy best practices
- Appropriate CHECK constraints are defined where needed

**Testing:**
- [ ] Write unit tests for each account model verifying inheritance works properly
- [ ] Test foreign key constraints and cascading behavior
- [ ] Test field constraints (e.g., nullable, defaults) with valid and invalid data
- [ ] Write integration tests for polymorphic queries on each model type

### 2.3 Modern Financial Services Models

- [ ] Implement PaymentAppAccount model with defined fields
  - platform, has_debit_card, card_last_four, linked_account_ids, supports_direct_deposit, supports_crypto
- [ ] Implement BNPLAccount model with all required fields
  - original_amount, installment_count, installments_paid, installment_amount, payment_frequency, next_payment_date, promotion_info, late_fee, bnpl_provider
- [ ] Implement EWAAccount model with defined fields
  - provider, max_advance_percentage, per_transaction_fee, pay_period_start, pay_period_end, next_payday
- [ ] Ensure all models inherit properly from Account base model
- [ ] Verify polymorphic_identity is correctly set for each model
- [ ] Configure appropriate nullable constraints on required fields

**Verification:**
- All model fields match ADR-019 specifications
- Database migration script creates all required tables and columns
- Foreign key relationships are properly configured
- Models follow SQLAlchemy best practices
- Field constraints match business rules

**Testing:**
- [ ] Write unit tests for each modern account model
- [ ] Test special business logic for BNPL lifecycle management
- [ ] Test relationships between PaymentApp and linked accounts
- [ ] Write integration tests for polymorphic queries
- [ ] Test validation constraints at the database level

### 2.4 Database Migration Script

- [ ] Create Alembic migration script for all new tables and columns
- [ ] Include creation of required indexes
- [ ] Ensure proper foreign key relationships in the migration
- [ ] Verify migration can be applied to clean database
- [ ] Verify migration can be rolled back without data loss
- [ ] Add feature flag checks in data access code

**Verification:**
- Migration script runs successfully
- All tables and columns are created with correct types
- Indexes are properly created
- Foreign keys are properly configured
- Rollback works correctly

**Testing:**
- [ ] Test migration with empty database
- [ ] Test rollback functionality
- [ ] Verify all constraints are properly created
- [ ] Test with feature flags enabled and disabled

## Phase 3: Pydantic Schema Implementation

### 3.1 Base Schema Enhancements

- [ ] Update AccountBase, AccountCreate, and AccountResponse schemas as needed
- [ ] Ensure proper MoneyDecimal and PercentageDecimal usage as per ADR-013
- [ ] Verify field validators follow Pydantic V2 patterns with @field_validator
- [ ] Add appropriate validators for currency and international fields
- [ ] Implement proper date validation for all datetime fields
- [ ] Add documentation alongside schema implementation

**Verification:**
- Schemas correctly use MoneyDecimal and PercentageDecimal types
- Validators follow Pydantic V2 pattern with @classmethod and @field_validator
- All required fields are present
- Class Config uses orm_mode=True for response schemas
- Schemas follow ADR-012 validation layer standards

**Testing:**
- [ ] Write unit tests for base schemas with valid and invalid data
- [ ] Test datetime field validation for timezone awareness
- [ ] Test currency field validation with various currency codes
- [ ] Test schema validation error messages for clarity
- [ ] Verify feature flag integration with schema validation

### 3.2 Traditional Banking Account Schemas

- [ ] Implement CheckingAccountCreate and CheckingAccountResponse schemas
  - Include validators for routing_number format
  - Add validator for overdraft_limit when has_overdraft_protection is True
  - Add validators for international banking fields
- [ ] Implement SavingsAccountCreate and SavingsAccountResponse schemas
  - Include validators for interest_rate (must be valid percentage)
  - Add validator for compound_frequency (must be valid option)
- [ ] Implement CreditAccountCreate and CreditAccountResponse schemas
  - Include validators for credit_limit (must be positive)
  - Add validators for statement_balance, minimum_payment
  - Add validator for autopay_status (must be valid option)
- [ ] Create documentation alongside schema implementation

**Verification:**
- All schemas include appropriate Literal["account_type"] field
- Validators properly enforce business rules
- Error messages are clear and actionable
- Response schemas include all fields from models
- Create schemas include appropriate defaults

**Testing:**
- [ ] Write unit tests for each schema's validators
- [ ] Test all validation rules with valid and invalid data
- [ ] Test error messages for clarity and accuracy
- [ ] Test inheritance behavior from base schemas
- [ ] Verify field constraints match business requirements

### 3.3 Modern Financial Services Schemas

- [ ] Implement PaymentAppAccountCreate and PaymentAppAccountResponse schemas
  - Include validator for platform (must be in list of valid platforms)
  - Add validator for card_last_four format when has_debit_card is True
- [ ] Implement BNPLAccountCreate and BNPLAccountResponse schemas
  - Include validators for installment_count (must be positive)
  - Add validator for payment_frequency (must be valid option)
  - Add validator for next_payment_date (must be in future for new accounts)
- [ ] Implement EWAAccountCreate and EWAAccountResponse schemas
  - Include validator for max_advance_percentage (must be 0-100%)
  - Add validator for next_payday (must be in future for new accounts)
- [ ] Create documentation alongside schema implementation

**Verification:**
- All schemas include appropriate Literal["account_type"] field
- Validators properly enforce business rules
- Error messages are clear and actionable
- Response schemas include all fields from models
- Create schemas include appropriate defaults

**Testing:**
- [ ] Write unit tests for each schema focusing on unique validations
- [ ] Test BNPL-specific validations for installments and payments
- [ ] Test PaymentApp platform validation with valid and invalid values
- [ ] Test date validations for EWA payday requirements
- [ ] Test internationalization aspects of schemas

### 3.4 Discriminated Union Implementation

- [ ] Implement BankingAccountCreateUnion using Pydantic's Annotated and Union
- [ ] Implement BankingAccountResponseUnion using Pydantic's Annotated and Union
- [ ] Ensure all account types are included in the unions
- [ ] Set up proper discriminator configuration
- [ ] Create documentation for union type usage

**Verification:**
- Union types include all account subtypes
- Field(discriminator="account_type") is configured
- Union types work correctly with FastAPI
- Serialization and deserialization work as expected

**Testing:**
- [ ] Test serialization and deserialization of each account type via the union
- [ ] Test discriminator behavior with various account types
- [ ] Test API integration with the union types
- [ ] Test with feature flags to verify behavior when types are disabled
- [ ] Write integration tests for end-to-end schema validation

## Phase 4: Repository Layer Implementation

### 4.1 Account Repository Enhancements

- [ ] Extend AccountRepository with banking-specific methods
- [ ] Implement methods to retrieve accounts by specific types
- [ ] Implement methods for upcoming payments across account types
- [ ] Add specialized queries for banking account reporting
- [ ] Implement proper error handling for repository operations
- [ ] Add feature flag checks in repository methods
- [ ] Create documentation alongside repository implementation

**Verification:**
- Repository extends BaseRepository
- Repository methods use appropriate SQLAlchemy patterns
- Methods follow naming conventions
- Transaction boundaries are properly managed
- Query performance is considered with appropriate join strategies
- Error handling follows established patterns

**Testing:**
- [ ] Write unit tests for each new repository method
- [ ] Test with real database and real data
- [ ] Test query performance with larger datasets
- [ ] Verify proper error handling with edge cases
- [ ] Test with feature flags enabled and disabled

### 4.2 Type-Specific Repository Methods

- [ ] Implement get_checking_accounts_by_user method
- [ ] Implement get_credit_accounts_with_upcoming_payments method
- [ ] Implement get_bnpl_accounts_with_upcoming_payments method
- [ ] Implement get_connected_payment_app_accounts method
- [ ] Ensure all methods handle is_closed flag appropriately
- [ ] Create documentation alongside method implementation

**Verification:**
- Methods use appropriate SQLAlchemy querying techniques
- Methods return strongly typed results
- Methods handle error cases properly
- Complex queries use appropriate join strategies
- Results are ordered appropriately where needed

**Testing:**
- [ ] Write unit tests for each type-specific repository method
- [ ] Test with various account statuses (open, closed)
- [ ] Test with realistic data including multiple account types
- [ ] Verify order and filtering work correctly
- [ ] Test performance with larger datasets
- [ ] Test edge cases like no accounts found

### 4.3 Integration with Bill Split Repository

- [ ] Update BillSplitRepository to work with polymorphic account types
- [ ] Add validation for eligible account types for bill splits
- [ ] Implement methods to retrieve bill splits by account type
- [ ] Ensure proper transaction handling for bill splits
- [ ] Create documentation for bill split integration

**Verification:**
- BillSplitRepository works correctly with all account types
- Foreign key relationships are handled properly
- Queries join correctly to polymorphic account tables
- Transaction boundaries are properly defined
- Method signatures follow repository pattern

**Testing:**
- [ ] Test bill splits with each eligible account type
- [ ] Test validation rules for ineligible account types
- [ ] Test transaction handling across multiple entities
- [ ] Verify polymorphic queries return correct bill splits
- [ ] Test with feature flags to ensure proper integration

## Phase 5: Service Layer Implementation

### 5.1 Account Service Enhancements

- [ ] Extend AccountService with banking-specific methods
- [ ] Implement get_upcoming_payments method
- [ ] Implement get_banking_overview method
- [ ] Implement update_bnpl_status method
- [ ] Add comprehensive error handling with specific error classes
- [ ] Integrate with feature flag system
- [ ] Create documentation alongside service implementation

**Verification:**
- Service injects repository dependencies
- Methods validate input parameters
- Business rules are properly implemented
- Error handling uses appropriate error classes
- Methods return appropriate types
- No direct ORM operations in service methods

**Testing:**
- [ ] Write unit tests for all service methods
- [ ] Test business rule validation
- [ ] Test with feature flags enabled and disabled
- [ ] Test error handling for various scenarios
- [ ] Test aggregation and calculation logic
- [ ] Test lifecycle management of temporary accounts (BNPL)

### 5.2 Business Logic Implementation

- [ ] Implement balance calculation logic for different account types
- [ ] Implement due date tracking across account types
- [ ] Implement account lifecycle management (especially for BNPL)
- [ ] Implement validation rules for account operations
- [ ] Create documentation for business logic

**Verification:**
- Balance semantics are handled correctly for each account type
- Due date calculations follow ADR-011 datetime standards
- Lifecycle transitions are properly managed
- Validation rules match business requirements
- Methods return appropriate error messages

**Testing:**
- [ ] Test balance calculations for assets vs. liabilities
- [ ] Test due date tracking with datetime manipulation
- [ ] Test BNPL lifecycle from creation through completion
- [ ] Test validation rules with valid and invalid data
- [ ] Write integration tests for end-to-end business flows
- [ ] Test edge cases like account status changes

### 5.3 Error Handling Implementation

- [ ] Implement hierarchical error structure as defined in ADR-019
- [ ] Create specific error classes for validation failures
- [ ] Implement type-specific error classes
- [ ] Ensure error messages are clear and actionable
- [ ] Document error handling strategy and usage

**Verification:**
- Error hierarchy matches ADR-019 specification
- Error classes include appropriate codes and HTTP status codes
- Error messages are user-friendly
- Type-specific errors provide detailed information
- Errors are properly propagated through the service layer

**Testing:**
- [ ] Write unit tests for each error class
- [ ] Test error propagation through service layers
- [ ] Test error message clarity and actionability
- [ ] Test error handling in edge cases
- [ ] Verify error responses match expected format
- [ ] Test internationalization of error messages

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
- Endpoints use appropriate HTTP methods
- Response models match repository/service returns
- Input validation uses Pydantic schemas
- Endpoints include appropriate OpenAPI documentation
- Authentication and authorization are properly enforced

**Testing:**
- [ ] Write integration tests for each API endpoint
- [ ] Test authentication and authorization scenarios
- [ ] Test with valid and invalid input data
- [ ] Test with feature flags enabled and disabled
- [ ] Verify error responses match expected format
- [ ] Load test endpoints with realistic traffic volumes

### 6.2 Account Type Registry Integration

- [ ] Update AccountTypeRegistry initialization with new account types
- [ ] Register all banking account types with appropriate metadata
- [ ] Implement API endpoint to retrieve available account types
- [ ] Implement API endpoint to retrieve account types by category

**Verification:**
- Registry includes all account types defined in ADR-019
- Registration includes model_class, schema_class, name, description, category
- API endpoints return correct account type information
- Registry handles unknown types gracefully

### 6.3 Error Response Formatting

- [ ] Implement consistent error response format
- [ ] Map specific error classes to HTTP status codes
- [ ] Ensure error details include field-level information where appropriate
- [ ] Test error responses for various failure scenarios

**Verification:**
- Error responses follow the format defined in ADR-019
- HTTP status codes match error types
- Error messages are clear and actionable
- Validation errors include field-specific details
- Error handling doesn't expose sensitive information

## Phase 7: Performance Optimization

### 7.1 Database Optimization

- [ ] Implement comprehensive indexing strategy
- [ ] Add denormalization fields for frequent queries
- [ ] Implement query caching for frequently accessed data
- [ ] Configure appropriate connection pooling
- [ ] Document optimization strategies

**Verification:**
- Indexes are created for common query patterns
- Denormalization fields are updated consistently
- Cache invalidation works correctly
- Connection pooling is configured appropriately

**Testing:**
- [ ] Benchmark common queries with and without optimizations
- [ ] Test cache hit/miss scenarios
- [ ] Verify index usage with query plans
- [ ] Load test with concurrent connections
- [ ] Test with larger datasets to verify scaling
- [ ] Verify feature flag impact on query patterns

### 7.2 Query Optimization

- [ ] Implement selective loading for polymorphic queries
- [ ] Optimize complex joins for performance
- [ ] Implement pagination for list endpoints
- [ ] Add result limiting for large queries
- [ ] Document query optimization patterns

**Verification:**
- Selective loading reduces query complexity
- Complex joins use efficient query patterns
- Pagination works correctly for all list endpoints
- Large result sets are properly limited

**Testing:**
- [ ] Benchmark query performance with different strategies
- [ ] Test pagination with large datasets
- [ ] Verify query plans for optimal execution
- [ ] Test with realistic data volumes
- [ ] Measure memory usage for large queries

### 7.3 Load Testing and Stress Testing

- [ ] Develop realistic load testing scenarios
- [ ] Test system behavior under normal load
- [ ] Test system behavior under peak load
- [ ] Identify and address performance bottlenecks
- [ ] Document performance characteristics and limits

**Verification:**
- System handles expected load without degradation
- Response times remain within acceptable limits
- Resource usage scales predictably with load
- System gracefully handles load spikes

**Testing:**
- [ ] Run load tests with simulated user traffic
- [ ] Test concurrent read and write operations
- [ ] Measure and analyze response time distributions
- [ ] Identify degradation points and recovery behavior
- [ ] Test with feature flags to assess impact on performance

## Phase 8: Documentation and Feature Management

### 8.1 Code Documentation Finalization

- [ ] Review and complete docstrings for all public methods
- [ ] Document class inheritance relationships
- [ ] Document error handling strategies
- [ ] Add examples for complex operations
- [ ] Verify documentation for all new components

**Verification:**
- All public classes and methods have docstrings
- Parameter and return types are documented
- Complex logic is explained with comments
- Error conditions are documented
- Examples are provided for complex operations

**Testing:**
- [ ] Verify docstring format meets project standards
- [ ] Test examples in docstrings for correctness
- [ ] Check for missing documentation
- [ ] Verify type annotations match documentation

### 8.2 API Documentation

- [ ] Update OpenAPI schema with new endpoints
- [ ] Document request and response models
- [ ] Include examples for each endpoint
- [ ] Document error responses with status codes
- [ ] Verify documentation is accurate and complete

**Verification:**
- OpenAPI schema includes all new endpoints
- Request and response models are fully documented
- Examples include realistic data
- Error responses are documented with status codes
- Authentication requirements are clearly specified

**Testing:**
- [ ] Verify generated API documentation
- [ ] Test examples in documentation
- [ ] Review documentation for accuracy
- [ ] Check for missing endpoints or parameters

### 8.3 Feature Flag Configuration

- [ ] Configure banking account types feature flag
- [ ] Add appropriate default value (disabled in production)
- [ ] Implement monitoring for feature flag usage
- [ ] Develop rollout strategy for banking account types
- [ ] Create rollback plan in case of issues

**Verification:**
- Feature flag is correctly configured
- Default values are appropriate for each environment
- Monitoring captures flag state and usage
- Rollout strategy is documented
- Rollback plan is tested

**Testing:**
- [ ] Test behavior with feature flag enabled
- [ ] Test behavior with feature flag disabled
- [ ] Test toggle during runtime
- [ ] Verify monitoring captures flag usage
- [ ] Test rollback procedures

## Phase 9: Final Verification and Release

### 9.1 Integration Testing

- [ ] Perform end-to-end integration testing
- [ ] Test all account types and their interactions
- [ ] Verify bill split integration works correctly
- [ ] Test international banking features
- [ ] Test edge cases specific to each account type

**Verification:**
- All components work together correctly
- Data flows correctly through all layers
- Error handling works end-to-end
- Feature flags control access to new functionality

**Testing:**
- [ ] Test complete user workflows
- [ ] Test with realistic data sets
- [ ] Test cross-account interactions
- [ ] Verify error propagation through all layers
- [ ] Test with different feature flag configurations

### 9.2 Security Review

- [ ] Perform security audit of new code
- [ ] Verify authentication and authorization
- [ ] Check for potential SQL injection vulnerabilities
- [ ] Review error handling for information leakage
- [ ] Verify sensitive data protection

**Verification:**
- Authentication is required for all endpoints
- Authorization checks prevent unauthorized access
- Error messages don't reveal sensitive information
- Sensitive data is properly protected
- Input validation prevents injection attacks

**Testing:**
- [ ] Test authentication bypass attempts
- [ ] Test authorization with different user roles
- [ ] Test with malicious input data
- [ ] Verify error responses don't leak sensitive information
- [ ] Test for common OWASP vulnerabilities

### 9.3 Code Quality Review

- [ ] Verify compliance with ADR-011 (DateTime Standardization)
  - All datetime fields use UTC
  - No naive datetime objects are created
  - All date/time operations use utilities from datetime_utils.py

- [ ] Verify compliance with ADR-012 (Validation Layer)
  - Models only contain constraints, no business logic
  - Schemas handle data structure validation
  - Service layer implements business rules

- [ ] Verify compliance with ADR-013 (Decimal Precision)
  - Monetary values use Numeric(12, 4) in database
  - API boundaries enforce 2 decimal places
  - Schemas use MoneyDecimal and PercentageDecimal types

- [ ] Verify compliance with ADR-014 (Repository Layer)
  - Repositories extend BaseRepository
  - Repositories focus on data access, not business logic
  - Transaction boundaries are properly managed

- [ ] Verify compliance with ADR-016 (Account Type Expansion)
  - Polymorphic inheritance is correctly implemented
  - Account Type Registry is properly used
  - Schema inheritance matches model inheritance

- [ ] Verify compliance with ADR-019 (Banking Account Types)
  - All specified account types are implemented
  - Business rules are properly enforced
  - International support is implemented
  - Error handling follows defined strategy

- [ ] Verify compliance with ADR-024 (Feature Flag System)
  - Feature flags are correctly integrated
  - Conditional logic respects feature flag state
  - Feature flags control access to new functionality
  - Documentation explains feature flag usage

**Verification:**
- All code follows established patterns
- No violations of architectural principles
- Consistent implementation across components
- Documentation matches implementation

**Testing:**
- [ ] Run static code analysis tools
- [ ] Perform code review with multiple reviewers
- [ ] Verify automated tests cover all requirements
- [ ] Check all ADR compliance points

### 9.4 Release Preparation

- [ ] Finalize feature flag configuration for release
- [ ] Create release notes
- [ ] Prepare database initialization scripts
- [ ] Develop rollout plan with phased approach
- [ ] Create monitoring dashboards for new features

**Verification:**
- Release notes document all new features
- Database scripts initialize required data
- Rollout plan includes fallback options
- Monitoring captures key metrics

**Testing:**
- [ ] Test release process in staging environment
- [ ] Verify database initialization works correctly
- [ ] Test rollout plan including rollback scenarios
- [ ] Verify monitoring captures appropriate metrics
- [ ] Perform final end-to-end tests with production configuration
