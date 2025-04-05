# Active Context: Debtonator

## Current Focus

Account Type Expansion, Service Layer Implementation, Feature Flag System, Banking Account Types Integration, Testing Strategy Implementation, ADR Implementation Checklists, UTC DateTime Standardization Fixes

### Recent Changes

1. **Fixed UTC Timezone Validation and Datetime Handling Issues (April 5, 2025)** ✓
   - Fixed `LiabilityDateRange` validator to properly handle timezone-aware comparisons
   - Changed field validator to model validator with proper `ensure_utc()` calls
   - Fixed SQLAlchemy column validation to avoid direct boolean evaluation
   - Ensured all test classes use `utc_now()` instead of `datetime.now()` for default factories
   - Created missing `DepositScheduleResponse` schema with proper field definitions
   - Updated test assertions to match Pydantic v2's error message format
   - Ensured all datetime validation follows ADR-011 requirements
   
2. **Implemented Service Layer for Account Types and Fixed Pydantic v2 Discriminated Union Issues (April 4, 2025)** ✓
   - Moved account type validation from schemas to service layer to resolve conflict with Pydantic discriminated unions
   - Enhanced feature flag integration in account creation and validation workflows
   - Implemented `get_banking_overview` and related methods for comprehensive financial data across all account types
   - Added support for type-specific account handling via the feature flag-aware type registry system
   - Fixed polymorphic schema validation issues with discriminated unions in Pydantic v2:
     - Removed wildcard `field_validator("*", mode="before")` that conflicted with discriminator fields
     - Changed inheritance order in all account response classes to prioritize concrete types with Literal fields
     - Added explicit redeclaration of discriminator fields in response classes
     - Used model-level validators with `mode="after"` instead of field-level validators
     - Documented the pattern in system_patterns.md for future reference

3. **Implemented Repository Layer Tests for Account Types (April 3, 2025)** ✓
   - Created comprehensive integration tests for the modular repository pattern
   - Implemented tests for repository factory with dynamic module loading
   - Added tests for checking, savings, and credit account repositories
   - Created feature flag integration tests for banking account types
   - Added tests for bill splits with polymorphic account types
   - Implemented tests for proper transaction boundaries and error handling
   - Verified proper relationship loading across polymorphic types
   - Added test coverage for feature flag effects on account creation and querying
   - Created specialized test fixtures for each account type
   - Established organized test package structure with proper __init__.py files

4. **Fixed Polymorphic Identity Warnings and Test Layer Separation (April 3, 2025)** ✓
   - Resolved SQLAlchemy warnings about incompatible polymorphic identity
   - Updated account fixtures to use proper polymorphic subclasses (CheckingAccount, SavingsAccount, CreditAccount)
   - Moved service-dependent tests from model unit tests to integration test files
   - Fixed test failures in CashflowForecast model tests
   - Added "Polymorphic Identity Pattern" section to system_patterns.md
   - Added "Test Layer Separation" section to document layer boundary principles
   - Enforced proper test organization with model tests focused on model behavior only
   - Ensured integration tests are properly located for cross-layer testing
   - Created mermaid diagrams illustrating both patterns for documentation
   - Fixed discriminator value warnings in payment tests

5. **Fixed SQLAlchemy 2.0 Compatibility in Account Type Tests (April 3, 2025)** ✓
   - Restructured test fixtures to use proper polymorphic account type hierarchy
   - Created mirrored fixture directory structure matching source code organization
   - Updated SQLAlchemy query API from legacy to 2.0 syntax for compatibility with AsyncSession
   - Fixed test fixtures for all banking account types (checking, savings, credit, bnpl, ewa, payment_app)
   - Resolved CI failure in unit tests for account types
   - Updated system_patterns.md with modern SQLAlchemy query patterns
   - Enhanced tech_context.md with explicit SQLAlchemy 2.0 and Pydantic 2.0 references
   - Fixed CI/CD pipeline to run all tests successfully
   - Implemented proper test fixture pattern for all account types
   - Created consistent pattern for account type testing

## Next Steps

1. **Investigate Account Type Update Restrictions**
   - Evaluate architectural implications of updating account_type field
   - Account type changes affect DB storage location (polymorphic inheritance)
   - Different account types have different validation rules and required fields
   - Consider implementing formal account type conversion workflow with proper data migration
   - Add validation at service layer to prevent direct account_type updates
   - Document account type transition policy in ADR
   - Define allowed account type transitions based on business rules
   - Consider implementing a specialized AccountConversionService
   - Evaluate impact on historical data and reporting

2. **Complete API Layer Integration**
   - Implement GET /banking/overview endpoint
   - Create GET /banking/upcoming-payments endpoint
   - Add POST /accounts/banking endpoint 
   - Implement POST /accounts/bnpl/{account_id}/update-status endpoint
   - Create endpoints to retrieve available account types
   - Add feature flag integration to API endpoints
   - Create OpenAPI documentation

2. **Implement Error Handling System**
   - Create account-specific error hierarchy in errors/ module
   - Implement AccountError base class and specialized subclasses
   - Add feature flag-related error classes
   - Create consistent error formatting across layers
   - Implement error translation between layers
   - Add user-friendly error messages to API responses

3. **Complete API Layer Tests**
   - Create integration tests for API endpoints with all account types
   - Test polymorphic request and response validation
   - Implement tests for feature flag integration at API layer
   - Add tests for error handling and status codes
   - Test authentication and authorization scenarios
   - Create tests for different feature flag states
   - Add tests for multi-currency and international field handling

4. **Update Test Cases for Polymorphic Validation**
   - Extend test coverage for the new Pydantic v2 discriminated union pattern
   - Create comprehensive test cases for all account types
   - Test proper handling of inheritance and discriminator fields
   - Add tests for model validation in discriminated union context
   - Ensure test factory compatibility with discriminated union models

5. **Complete Schema Factory Development**
   - Implement schema factories for all account types
   - Add support for customization via kwargs
   - Create factories for testing with appropriate defaults
   - Support international banking field generation
   - Add feature flag awareness to factories
   - Test factory output with validation

## Implementation Lessons

1. **Testing Structured Directory Pattern**
   - Mirror the exact source directory structure in test files:

   ```python
   src/schemas/account_types/banking/checking.py
   -> tests/unit/schemas/account_types/banking/test_checking.py
   ```

   - Separate test files per component keeps tests focused and maintainable
   - Use descriptive test method names that describe the behavior being tested
   - Tests should focus on one aspect of functionality per test method
   - Create proper test package structure with `__init__.py` files
   - Test lower layers thoroughly before moving to higher layers

2. **Polymorphic Schema Pattern with Pydantic V2**
   - Use Literal fields to enforce discriminator values in derived schemas:

   ```python
   # Base schema allows any valid account_type
   class AccountBase(BaseSchemaValidator):
       account_type: str = Field(..., description="Type of account")
   
   # Derived schema enforces a specific account_type
   class CheckingAccountBase(AccountBase):
       account_type: Literal["checking"] = "checking"
   ```

   - Use Annotated with Union and Field(discriminator=) for polymorphic API schemas:

   ```python
   from typing import Annotated, Union
   from pydantic import Field

   AccountCreateUnion = Annotated[
       Union[
           CheckingAccountCreate,
           SavingsAccountCreate,
           CreditAccountCreate,
       ],
       Field(discriminator="account_type")
   ]
   ```

   - With discriminated unions, client only needs to set account_type and other fields
   - API will automatically deserialize to the correct schema class
   - Always document discriminator field usage in schema docstrings

3. **Feature Flag Layer Integration**
   - Feature flags should be evaluated at the service layer, not directly in repositories
   - Integration tests for feature flags should test full flow from config to database
   - Flag values should be synchronized between registry (memory) and repository (database)
   - Design feature flags to handle context-specific evaluation
   - Use composition to build complex flag evaluation logic
   - Test both enabled and disabled states for proper flag behavior

   ```python
   # Feature flag service integration in service layer
   def get_available_account_types(self, user_id: int) -> List[Dict[str, Any]]:
       # Check if banking account types are enabled
       if not self.feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
           # Return only basic account types if feature is disabled
           return self.registry.get_types_by_category("Basic")
       
       # Return all account types when feature is enabled
       return self.registry.get_all_types()
   ```

4. **Discriminator Field Validator Pattern**
   - Move validators away from discriminator fields to prevent conflict with Pydantic v2:

   ```python
   # Incorrect - validator on discriminator field:
   class AccountBase(BaseSchemaValidator):
       account_type: str = Field(..., description="Type of account")
       
       @field_validator("account_type")
       @classmethod
       def validate_account_type(cls, v):
           # Validation logic
           return v
           
   # Correct - move validation to service layer:
   class AccountService:
       def create_account(self, account_data: AccountCreateUnion) -> AccountResponseUnion:
           account_type = account_data.account_type
           if not self.is_valid_account_type(account_type):
               raise ValueError(f"Invalid account type: {account_type}")
   ```

   - For discriminated unions, validators cannot operate on the discriminator field
   - Move complex validation logic to the service layer
   - Use Literal types to enforce discriminator values in schema classes
   - Ensure error messages are consistent between schema and service validation
   - Document validation approach for discriminated unions

5. **Real Objects Testing Philosophy**
   - Never use mocks in tests - unittest.mock and MagicMock are strictly prohibited:

   ```python
   # Incorrect - using mocks:
   mock_repo = MagicMock()
   mock_repo.get.return_value = None
   service = AccountService(mock_repo)
   
   # Correct - using real objects:
   repo = AccountRepository(db_session)
   service = AccountService(repo)
   ```

   - Always use real repositories with the test database
   - Test database gets set up and torn down between each test
   - Test real cross-layer interactions instead of isolating components
   - Create real test data through schema factories and repository methods
   - Use real schema validation in every test
   - Integration-first approach gives higher confidence in production behavior

6. **Type-Specific Validator Methods**
   - Implement cross-field validation using model validators:

   ```python
   @field_validator("overdraft_limit")
   @classmethod
   def validate_overdraft_limit(cls, value: Optional[Decimal], info: ValidationInfo) -> Optional[Decimal]:
       has_protection = info.data.get("has_overdraft_protection", False)
       
       if has_protection and value is None:
           raise ValueError("Overdraft limit is required when overdraft protection is enabled")
           
       if not has_protection and value is not None:
           raise ValueError("Overdraft limit cannot be set when overdraft protection is disabled")
           
       return value
   ```

   - Validate complex business rules at the model level, not individual fields
   - Error messages should be clear and actionable
   - Use validation context (info.data) to access other field values
   - Always check for None values to handle partial updates
   - Consider the impact of concurrent validation on dependent fields
   - Each validator should focus on a single responsibility

7. **Safe Datetime Comparison**
   - Use `ensure_utc()` to normalize datetimes before comparison:

   ```python
   # Incorrect - direct comparison can fail with timezone mismatches
   if end_date <= start_date:
       raise ValueError("End date must be after start date")
   
   # Correct - ensure both dates have UTC timezone
   start_date = ensure_utc(self.start_date)
   end_date = ensure_utc(self.end_date)
   
   if end_date <= start_date:
       raise ValueError("End date must be after start date")
   ```

   - Use model validators instead of field validators for cross-field validation
   - Ensure all datetime comparisons handle timezone-aware and naive objects properly
   - Use utility functions consistently (utc_now(), utc_datetime(), etc.)
   - Follow ADR-011 recommendations consistently across the codebase
