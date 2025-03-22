## Implementation Guide: Repository Test Pattern

### The Arrange-Schema-Act-Assert Pattern

All repository tests must follow the Arrange-Schema-Act-Assert pattern to properly simulate the validation flow in our application:

1. **Arrange**: Set up any test fixtures and dependencies needed for the test.
2. **Schema**: Create and validate data through appropriate Pydantic schemas.
3. **Act**: Convert validated schemas to dictionaries and pass to repository methods.
4. **Assert**: Verify that the repository operation produced the expected results.

Follow this template for all repository tests:

```python
@pytest.mark.asyncio
async def test_repository_operation(repo_fixture, other_fixtures):
    \"\"\"Test description that explains the purpose of the test.\"\"\"
    # 1. ARRANGE: Setup any test dependencies
    # ... setup code
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    entity_schema = create_entity_schema(
        key1=\"value1\",
        key2=\"value2\"
    )
    
    # Convert validated schema to dict for repository
    validated_data = entity_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    result = await repository.method(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.key1 == \"value1\"
    assert result.key2 == \"value2\"
```

Refer to `tests/integration/repositories/test_balance_reconciliation_repository.py` for a complete reference implementation of this pattern.

### Schema Factory Implementation

Instead of creating separate implementations for each repository test, use schema factories to create valid schema instances:

1. **Consult the Schema Factories Directory**: See `tests/helpers/schema_factories/` for existing factories.

2. **Add New Factory Functions When Needed**: When testing a repository that needs a new schema factory:
   - Create or update the appropriate domain file in `schema_factories/`
   - Add the factory function following the established pattern
   - Export the function in `__init__.py`

3. **Use Factories in Tests**: Import and use factory functions in your tests:
   ```python
   from tests.helpers.schema_factories import create_entity_schema
   
   entity_schema = create_entity_schema(name=\"Test\", value=100)
   ```

4. **Follow Factory Function Guidelines**:
   - Provide reasonable defaults for all non-required fields
   - Use type hints for parameters and return values
   - Document parameters, defaults, and return types
   - Allow overriding any field with `**kwargs`
   - Return validated schema instances, not dictionaries

Check the README.md in the schema_factories directory for detailed guidelines.

## Testing Checklist

For each repository test file:

- [ ] Review existing tests against the Arrange-Schema-Act-Assert pattern
- [ ] Identify missing schema factories required for tests
- [ ] Create or update schema factories as needed
- [ ] Refactor tests to use schema factories
- [ ] Ensure all CRUD operations include schema validation
- [ ] Add tests for validation error scenarios
- [ ] Add tests for repository-specific methods

## Implementing New Repositories

When implementing a new repository:

1. Create schema factories for associated model schemas
2. Write tests following the Arrange-Schema-Act-Assert pattern
3. Implement repository methods using TDD approach
4. Document any new patterns or optimizations

# ADR-014 Repository Layer Implementation Checklist

## Testing Strategy

1. **Validation Flow**
   - [x] Document validation strategy in ADR-014
   - [x] Update existing tests to simulate service layer validation
   - [x] All repository tests must pass data through Pydantic schemas first
   - [x] Use model_dump() to convert validated schema data to dict
   - [x] Add assertions to verify validation behavior

2. **Repository Test Template Pattern**
   - [x] Create reference pattern for consistent test structure
   - [x] Document the standard 4-step test pattern (Arrange-Schema-Act-Assert)
   - [x] Create a reference implementation in one repository test file
   - [x] Share the pattern with the team for standardization

3. **Integration Test Structure**
   - [x] Import appropriate schema files in each test module
   - [x] Create schema instances before calling repository methods
   - [x] Ensure all repository method calls use validated data
   - [x] Add validation-specific test cases
   - [x] Test error scenarios with invalid data that would be caught by schemas

4. **Test Factory Functions**
   - [x] Create factory functions that return validated schema instances
   - [x] Use factory functions in tests to reduce code duplication
   - [x] Provide factory customization options for test-specific scenarios
   - [x] Document factory function usage in test files

## Phase 1: Foundation Setup

1. **Directory Structure**
   - [x] Create `src/repositories` directory
   - [x] Create `src/repositories/__init__.py` file
   - [x] Create `src/repositories/base.py` for BaseRepository

2. **Base Repository Implementation**
   - [x] Implement `BaseRepository` class with generic type parameters
   - [x] Add CRUD operations:
     - [x] `create()` - Create a new record
     - [x] `get()` - Retrieve a single record by ID
     - [x] `get_multi()` - Retrieve multiple records with filtering
     - [x] `update()` - Update an existing record
     - [x] `delete()` - Delete a record

3. **Repository Factory**
   - [x] Create `src/repositories/factory.py`
   - [x] Implement `RepositoryFactory` class
   - [x] Add `get_repository()` method
   - [x] Add caching for repository instances

4. **Dependency Injection Setup**
   - [x] Create `src/api/dependencies/repositories.py`
   - [x] Implement repository provider functions
   - [x] Add dependency for AccountRepository
   - [x] Add dependency for LiabilityRepository
   - [x] Add dependency for PaymentRepository
   - [x] Add dependency for PaymentSourceRepository
   - [x] Add dependency for BillSplitRepository
   - [x] Add dependency for IncomeRepository
   - [x] Add dependency for RecurringBillRepository
   - [x] Add dependency for StatementHistoryRepository
   - [x] Add dependency for BalanceHistoryRepository
   - [x] Add dependency for CategoryRepository
   - [x] Add dependency for CreditLimitHistoryRepository
   - [x] Add dependency for BalanceReconciliationRepository
   - [x] Add dependency for TransactionHistoryRepository
   - [x] Add dependency for PaymentScheduleRepository
   - [x] Add dependency for DepositScheduleRepository

## Phase 2: Core Repositories

1. **Account Repository**
   - [x] Create `src/repositories/accounts.py`
   - [x] Implement `AccountRepository` class
   - [x] Add account-specific methods:
     - [x] `get_by_name()`
     - [x] `get_accounts_with_statements()`
     - [x] `get_active_accounts()`
     - [x] Additional methods (`get_with_relationships()`, `get_by_type()`, etc.)

2. **Bill Repository**
   - [x] Create `src/repositories/liabilities.py`
   - [x] Implement `LiabilityRepository` class
   - [x] Add bill-specific methods:
     - [x] `get_bills_due_in_range()`
     - [x] `get_bills_by_category()`
     - [x] `get_recurring_bills()`
     - [x] `get_with_splits()`
     - [x] `get_with_payments()`
     - [x] `get_with_relationships()`
     - [x] `find_bills_by_status()`
     - [x] `get_bills_for_account()`
     - [x] `get_upcoming_payments()`
     - [x] `get_overdue_bills()`
     - [x] `get_monthly_liability_amount()`
     - [x] `mark_as_paid()`
     - [x] `reset_payment_status()`

3. **Payment Repository**
   - [x] Create `src/repositories/payments.py`
   - [x] Implement `PaymentRepository` class
   - [x] Add payment-specific methods:
     - [x] `get_payments_for_bill()`
     - [x] `get_payments_for_account()`
     - [x] `get_payments_in_date_range()`
     - [x] `get_with_sources()`
     - [x] `get_with_relationships()`
     - [x] `get_payments_by_category()`
     - [x] `get_total_amount_in_range()`
     - [x] `get_recent_payments()`

4. **Payment Source Repository**
   - [x] Create `src/repositories/payment_sources.py`
   - [x] Implement `PaymentSourceRepository` class
   - [x] Add payment source-specific methods:
     - [x] `get_sources_for_payment()`
     - [x] `get_sources_for_account()`
     - [x] `bulk_create_sources()`
     - [x] `get_with_relationships()`
     - [x] `get_total_amount_by_account()`
     - [x] `delete_sources_for_payment()`

5. **Bill Split Repository**
   - [x] Create `src/repositories/bill_splits.py`
   - [x] Implement `BillSplitRepository` class
   - [x] Add bill split-specific methods:
     - [x] `get_splits_for_bill()`
     - [x] `get_splits_for_account()`
     - [x] `bulk_create_splits()`

6. **Income Repository**
   - [x] Create `src/repositories/income.py`
   - [x] Implement `IncomeRepository` class
   - [x] Add income-specific methods:
     - [x] `get_by_source()`
     - [x] `get_income_in_date_range()`
     - [x] `get_undeposited_income()`
     - [x] `get_income_by_account()`
     - [x] `get_total_undeposited()`
     - [x] `get_total_undeposited_by_account()`
     - [x] `get_with_relationships()`
     - [x] `get_income_by_category()`
     - [x] `mark_as_deposited()`
     - [x] `get_income_by_recurring()`
     - [x] `get_income_statistics_by_period()`
     - [x] `get_income_with_filters()`
     
7. **RecurringBill Repository**
   - [x] Create `src/repositories/recurring_bills.py`
   - [x] Implement `RecurringBillRepository` class
   - [x] Add recurring bill-specific methods:
     - [x] `get_by_name()`
     - [x] `get_active_bills()`
     - [x] `get_by_day_of_month()`
     - [x] `get_with_liabilities()`
     - [x] `get_with_account()`
     - [x] `get_with_category()`
     - [x] `get_with_relationships()`
     - [x] `get_by_account_id()`
     - [x] `get_by_category_id()`
     - [x] `find_bills_with_auto_pay()`
     - [x] `toggle_active()`
     - [x] `toggle_auto_pay()`
     - [x] `update_day_of_month()`
     - [x] `get_monthly_total()`
     - [x] `check_liability_exists()`
     - [x] `get_upcoming_bills()`
     
8. **StatementHistory Repository**
   - [x] Create `src/repositories/statement_history.py`
   - [x] Implement `StatementHistoryRepository` class
   - [x] Add statement history-specific methods:
     - [x] `get_by_account()`
     - [x] `get_latest_statement()`
     - [x] `get_with_account()`
     - [x] `get_by_date_range()`
     - [x] `get_statements_with_due_dates()`
     - [x] `get_upcoming_statements_with_accounts()`
     - [x] `get_statements_with_minimum_payment()`
     - [x] `get_average_statement_balance()`
     - [x] `get_statement_trend()`
     - [x] `get_minimum_payment_trend()`
     - [x] `get_total_minimum_payments_due()`
     - [x] `get_statement_by_date()`
     
9. **BalanceHistory Repository**
   - [x] Create `src/repositories/balance_history.py`
   - [x] Implement `BalanceHistoryRepository` class
   - [x] Add balance history-specific methods:
     - [x] `get_by_account()`
     - [x] `get_latest_balance()`
     - [x] `get_with_account()`
     - [x] `get_by_date_range()`
     - [x] `get_reconciled_balances()`
     - [x] `get_min_max_balance()`
     - [x] `get_balance_trend()`
     - [x] `get_average_balance()`
     - [x] `get_balance_history_with_notes()`
     - [x] `mark_as_reconciled()`
     - [x] `add_balance_note()`
     - [x] `get_missing_days()`
     - [x] `get_available_credit_trend()`
     
10. **Category Repository**
    - [x] Create `src/repositories/categories.py`
    - [x] Implement `CategoryRepository` class
    - [x] Add category-specific methods:
      - [x] `get_by_name()`
      - [x] `get_root_categories()`
      - [x] `get_with_children()`
      - [x] `get_with_parent()`
      - [x] `get_with_bills()`
      - [x] `get_with_relationships()`
      - [x] `get_children()`
      - [x] `get_ancestors()`
      - [x] `get_descendants()`
      - [x] `is_ancestor_of()`
      - [x] `move_category()`
      - [x] `get_category_path()`
      - [x] `find_categories_by_prefix()`
      - [x] `get_category_with_bill_count()`
      - [x] `get_categories_with_bill_counts()`
      - [x] `get_total_by_category()`
      - [x] `delete_if_unused()`

11. **CreditLimitHistory Repository**
    - [x] Create `src/repositories/credit_limit_history.py`
    - [x] Implement `CreditLimitHistoryRepository` class
    - [x] Add credit limit history-specific methods:
      - [x] `get_by_account()`
      - [x] `get_with_account()`
      - [x] `get_by_date_range()`
      - [x] `get_latest_limit()`
      - [x] `get_limit_at_date()`
      - [x] `get_limit_increases()`
      - [x] `get_limit_decreases()`
      - [x] `get_limit_change_trend()`
      - [x] `calculate_average_credit_limit()`

12. **BalanceReconciliation Repository**
    - [x] Create `src/repositories/balance_reconciliation.py`
    - [x] Implement `BalanceReconciliationRepository` class
    - [x] Add balance reconciliation-specific methods:
      - [x] `get_by_account()`
      - [x] `get_with_account()`
      - [x] `get_by_date_range()`
      - [x] `get_most_recent()`
      - [x] `get_largest_adjustments()`
      - [x] `get_total_adjustment_amount()`
      - [x] `get_adjustment_count_by_reason()`
      - [x] `get_reconciliation_frequency()`

13. **TransactionHistory Repository**
    - [x] Create `src/repositories/transaction_history.py`
    - [x] Implement `TransactionHistoryRepository` class
    - [x] Add transaction history-specific methods:
      - [x] `get_by_account()`
      - [x] `get_with_account()`
      - [x] `get_by_date_range()`
      - [x] `get_by_type()`
      - [x] `search_by_description()`
      - [x] `get_total_by_type()`
      - [x] `get_transaction_count()`
      - [x] `get_net_change()`
      - [x] `get_monthly_totals()`
      - [x] `get_transaction_patterns()`
      - [x] `bulk_create_transactions()`

## Required New Repositories

1. **Repository: DepositScheduleRepository**
   - [x] Create `src/repositories/deposit_schedules.py`
   - [x] Implement `DepositScheduleRepository` class
   - [x] Add deposit schedule-specific methods:
     - [x] `get_by_account()`
     - [x] `get_by_income()`
     - [x] `get_with_account()`
     - [x] `get_with_income()`
     - [x] `get_by_date_range()`
     - [x] `get_pending_schedules()`
     - [x] `get_processed_schedules()`
     - [x] `mark_as_processed()`
     - [x] `get_schedules_with_relationships()`
     - [x] Additional methods: `get_upcoming_schedules()`, `find_overdue_schedules()`, `get_recurring_schedules()`, `get_total_scheduled_deposits()`, `cancel_schedule()`, `update_status()`

2. **Repository: RecurringIncomeRepository**
   - [x] Create `src/repositories/recurring_income.py`
   - [x] Implement `RecurringIncomeRepository` class 
   - [x] Create `tests/helpers/schema_factories/recurring_income.py` schema factory
   - [x] Add recurring income-specific methods:
     - [x] `get_by_source()`
     - [x] `get_by_account()`
     - [x] `get_active_income()`
     - [x] `get_by_day_of_month()`
     - [x] `get_with_income_entries()`
     - [x] `get_with_account()`
     - [x] `get_with_category()`
     - [x] `get_with_relationships()`
     - [x] `toggle_active()`
     - [x] `toggle_auto_deposit()`
     - [x] `update_day_of_month()`
     - [x] `get_monthly_total()`
     - [x] Additional methods: `get_upcoming_deposits()`, `find_by_pattern()`, `get_total_by_source()`

3. **Repository: IncomeCategoryRepository**
   - [ ] Create `src/repositories/income_categories.py`
   - [ ] Implement `IncomeCategoryRepository` class
   - [x] Ensure schema factory exists for income categories
   - [ ] Add income category-specific methods:
     - [ ] `get_by_name()`
     - [ ] `get_with_income()`
     - [ ] `get_total_by_category()`
     - [ ] `get_categories_with_income_counts()`
     - [ ] `find_categories_by_prefix()`
     - [ ] `delete_if_unused()`
     - [ ] Additional methods: `get_active_categories()`, `get_categories_with_stats()`

4. **Repository: PaymentScheduleRepository**
   - [x] Create `src/repositories/payment_schedules.py`
   - [x] Implement `PaymentScheduleRepository` class
   - [x] Add payment schedule-specific methods:
     - [x] `get_by_account()`
     - [x] `get_by_liability()`
     - [x] `get_with_account()`
     - [x] `get_with_liability()`
     - [x] `get_by_date_range()`
     - [x] `get_pending_schedules()`
     - [x] `get_processed_schedules()`
     - [x] `mark_as_processed()`
     - [x] `get_schedules_with_relationships()`
     - [x] Additional methods: `get_upcoming_schedules()`, `find_overdue_schedules()`, `get_auto_process_schedules()`, `get_total_scheduled_payments()`, `cancel_schedule()`

5. **Repository: CashflowForecastRepository**
   - [ ] Create `src/repositories/cashflow.py`
   - [ ] Implement `CashflowForecastRepository` class
   - [x] Ensure schema factory exists in `tests/helpers/schema_factories/cashflow/forecasting.py`
   - [ ] Add cashflow forecast-specific methods:
     - [ ] `get_by_date()`
     - [ ] `get_by_date_range()`
     - [ ] `get_latest_forecast()`
     - [ ] `get_forecast_trend()`
     - [ ] `get_deficit_trend()`
     - [ ] `get_required_income_trend()`
     - [ ] `get_min_forecast()`
     - [ ] Additional methods: `get_forecast_with_metrics()`, `get_forecast_summary()`, `get_forecast_by_account()`

## Phase 3: Advanced Repository Features

1. **Pagination Support**
   - [x] Add `get_paginated()` method to BaseRepository
   - [x] Implement total count calculation
   - [x] Support for page and items_per_page parameters

2. **Advanced Querying**
   - [x] Add support for joins in BaseRepository
   - [x] Implement ordering support
   - [x] Add complex filtering capabilities

3. **Transaction Support**
   - [x] Implement `bulk_create()` method
   - [x] Add `bulk_update()` method
   - [x] Add transaction boundary support

4. **Relationship Loading**
   - [x] Add support for eager loading with joinedload
   - [x] Implement selectinload for collections
   - [x] Add options for controlling relationship loading

## Phase 4: Testing

1. **Test Fixtures**
   - [x] Create test database fixtures for repositories
   - [x] Implement repository test fixtures
   - [x] Implement complete test data generation
   - [x] Add common test utility functions

2. **Base Repository Tests**
   - [ ] Create `tests/unit/repositories/test_base_repository.py`
   - [ ] Test all CRUD operations
   - [ ] Test filtering and pagination

3. **Repository Test Pattern Implementation**
   - [x] Document the Arrange-Schema-Act-Assert pattern in `docs/guides/repository_test_pattern.md`
   - [x] Set up modular directory structure for schema factories
   - [x] Implement BalanceReconciliationRepository tests as the reference implementation
   - [ ] Review and refactor existing repository tests to follow the pattern
   - [ ] Ensure tests use schema factories to validate data before repository operations

4. **Schema Factory Implementation**
   - [x] Create modular directory structure for schema factories
   - [x] Create domain-specific factory files for each schema type
   - [x] Document factory creation guidelines in README
   - [x] Implement reusable factory functions with sensible defaults

5. **Integration Tests**
   - [ ] Ensure all integration tests follow the Arrange-Schema-Act-Assert pattern
   - [ ] Test transaction boundaries
   - [ ] Test complex query scenarios
   - [ ] Test error handling

6. **Model-Specific Repository Integration Tests**
   - [ ] Create/Update test file for AccountRepository
   - [ ] Create/Update test file for LiabilityRepository
   - [ ] Create/Update test file for PaymentRepository
   - [ ] Create/Update test file for PaymentSourceRepository
   - [ ] Create/Update test file for BillSplitRepository
   - [ ] Create/Update test file for RecurringBillRepository
   - [ ] Create/Update test file for StatementHistoryRepository
   - [ ] Create/Update test file for BalanceHistoryRepository
   - [ ] Create/Update test file for CategoryRepository
   - [ ] Create/Update test file for CreditLimitHistoryRepository
   - [x] Create/Update test file for BalanceReconciliationRepository
   - [ ] Create/Update test file for TransactionHistoryRepository
   - [ ] Create/Update test file for DepositScheduleRepository
   - [ ] Create test file for RecurringIncomeRepository (New)
   - [ ] Create test file for IncomeCategoryRepository (New)
   - [ ] Create/Update test file for PaymentScheduleRepository
   - [ ] Create test file for CashflowForecastRepository (New)
   - [ ] Implement comprehensive tests for model-specific methods
   - [ ] Test advanced querying features

## Phase 5: Service Refactoring

1. **Account Service Refactoring**
   - [x] Update `src/services/accounts.py` to use repositories
   - [x] Update service tests
   - [x] Validate refactored approach

2. **Bill Service Refactoring**
   - [ ] Update `src/services/bills.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

3. **Payment Service Refactoring**
   - [ ] Update `src/services/payments.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

4. **Bill Split Service Refactoring**
   - [ ] Update `src/services/bill_splits.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

5. **Income Service Refactoring**
   - [ ] Update `src/services/income.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

6. **Recurring Bill Service Refactoring**
   - [ ] Update `src/services/recurring_bills.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

7. **Payment Schedule Service Refactoring**
   - [x] Implement PaymentScheduleRepository (completed)
   - [ ] Create/Update `src/services/payment_schedules.py` to use repositories
   - [ ] Create/Update service tests
   - [ ] Validate approach

8. **Deposit Schedule Service Refactoring**
   - [x] Implement DepositScheduleRepository (completed)
   - [ ] Create/Update `src/services/deposit_schedules.py` to use repositories
   - [ ] Create/Update service tests
   - [ ] Validate approach

9. **Recurring Income Service Refactoring**
   - [ ] Create/Update `src/services/recurring_income.py` to use repositories
   - [ ] Create/Update service tests
   - [ ] Validate approach

10. **Cashflow Service Refactoring**
    - [ ] Create/Update `src/services/cashflow.py` to use repositories
    - [ ] Create/Update service tests
    - [ ] Validate approach

## Phase 6: Documentation and Finalization

1. **Repository Documentation**
   - [ ] Create usage documentation for repositories
   - [ ] Document common patterns and best practices
   - [ ] Add docstrings to all repository methods

2. **Service Documentation Updates**
   - [ ] Update service documentation to reflect new architecture
   - [ ] Document interaction between services and repositories
   - [ ] Create examples of service-repository usage

3. **API Documentation Updates**
   - [ ] Update API dependency documentation
   - [ ] Document service-repository interaction in API context
   - [ ] Update OpenAPI documentation

4. **Final Review and Testing**
   - [ ] Comprehensive integration testing
   - [ ] Performance testing for common operations
   - [ ] Code quality and linting review

## Implementation Strategy

1. **Create the Foundation First (COMPLETED)**
   - ✓ Implement the base repository layer
   - ✓ Create repository factory
   - ✓ Set up dependency injection
   - ✓ Write thorough tests for the base repository

2. **Build Key Repositories Incrementally (IN PROGRESS)**
   - ✓ Start with Account repository as it's fundamental
   - ✓ Implement Bill repository next (related to core functionality)
   - ✓ Add Payment and BillSplit repositories (core financial operations)
   - ✓ Implement remaining core repositories
   - ✓ Implement PaymentScheduleRepository and DepositScheduleRepository
   - ○ Implement remaining repositories (RecurringIncomeRepository, IncomeCategoryRepository, CashflowForecastRepository)

3. **Test Each Repository Thoroughly (IN PROGRESS)**
   - ✓ Create unit tests for specific repository features
   - ✓ Develop integration tests with real database fixtures
   - ○ Test transaction boundaries and error handling
   - ○ Verify advanced querying capabilities
   - ○ Create tests for newly implemented repositories

4. **Refactor One Service as Proof-of-Concept (COMPLETED)**
   - ✓ Choose a single service (Account service is recommended)
   - ✓ Refactor to use repositories
   - ✓ Validate approach with comprehensive tests
   - ✓ Document lessons learned for other service refactorings

5. **Gradually Refactor Remaining Services (IN PROGRESS)**
   - ✓ Use a consistent pattern based on the proof-of-concept
   - ○ Update each service individually
   - ○ Maintain thorough test coverage during refactoring
   - ○ Implement service integration for newly created repositories

## Implementation Priorities

Based on the current state of the repositories and ADR-014 implementation progress, the following priorities are recommended:

### High Priority Tasks (Required for ADR-014 Compliance)

1. **Complete Missing Repository Implementations**
   - [x] Implement `RecurringIncomeRepository` with standard methods
   - [ ] Implement `IncomeCategoryRepository` with standard methods
   - [ ] Implement `CashflowForecastRepository` with standard methods
   - [x] Create schema factory for `RecurringIncome` model

2. **Create Tests for New Repositories**
   - [ ] Create integration tests for `RecurringIncomeRepository`
   - [ ] Create integration tests for `IncomeCategoryRepository`
   - [ ] Create integration tests for `CashflowForecastRepository`
   - [ ] Create integration tests for recently implemented `DepositScheduleRepository`
   - [ ] Create integration tests for recently implemented `PaymentScheduleRepository`

3. **Service Layer Integration**
   - [ ] Create services to use the new repositories
   - [ ] Update API endpoints to use the new repositories via services
   - [ ] Ensure all services follow proper validation flow with Pydantic schemas

### Medium Priority Tasks (Recommended for Quality)

1. **Repository Tests Improvement**
   - [ ] Apply Arrange-Schema-Act-Assert pattern to all repository tests
   - [ ] Ensure all tests use schema factories
   - [ ] Add tests for transaction boundaries
   - [ ] Add tests for error handling

2. **Documentation**
   - [ ] Complete documentation for all repository methods
   - [ ] Document recommended patterns for repository usage
   - [ ] Update service documentation to reflect repository usage

### Lower Priority Tasks (Quality of Life)

1. **Performance Optimization**
   - [ ] Review query performance in complex repositories
   - [ ] Optimize relationship loading
   - [ ] Add caching where appropriate

2. **Extended Repository Features**
   - [ ] Add bulk operation methods to specialized repositories
   - [ ] Implement analytical queries for reporting functions
   - [ ] Add caching strategies for frequently used data
   - [ ] Support for complex filtering with multiple conditions

3. **Code Quality Improvements**
   - [ ] Add detailed docstrings to all repository methods
   - [ ] Standardize error handling across repositories
   - [ ] Implement logging for performance monitoring
   - [ ] Add code coverage metrics for repository tests

## Findings and Recommendations

Based on the comprehensive review of repositories against SQLAlchemy models, the following findings and recommendations are provided:

### Overall Findings

1. **Repository Implementation Status**
   - 15 of 18 required repositories are fully implemented
   - 3 repositories are still missing: 
     - RecurringIncomeRepository
     - IncomeCategoryRepository
     - CashflowForecastRepository

2. **Schema Factory Status**
   - Schema factories exist for most repository models
   - Missing schema factory for RecurringIncome model
   - Schema factories for CashflowForecast and IncomeCategory are in place

3. **Test Coverage Status**
   - Integration test coverage varies across repositories
   - New repositories (PaymentScheduleRepository, DepositScheduleRepository) lack test coverage
   - Not all existing tests follow the Arrange-Schema-Act-Assert pattern

4. **Service Integration Status**
   - AccountService successfully refactored to use repositories
   - Remaining services need refactoring to use the repository pattern
   - New services needed for PaymentSchedule and DepositSchedule

### Specific Recommendations

1. **Priority Implementation Tasks**
   - Implement the three missing repositories (RecurringIncome, IncomeCategory, CashflowForecast)
   - Create the missing schema factory for RecurringIncome
   - Develop integration tests for all new repositories
   - Create comprehensive docstrings for all repository methods

2. **Testing Improvements**
   - Apply the Arrange-Schema-Act-Assert pattern to all repository tests
   - Add test cases for transaction boundaries and error handling
   - Ensure all tests use schema factories for validation
   - Test relationship loading extensively

3. **Service Layer Enhancements**
   - Develop a consistent approach for service-repository integration
   - Update existing services to use repositories following AccountService pattern
   - Create new services for PaymentSchedule and DepositSchedule functionality
   - Ensure proper validation flow between schemas and repositories

4. **Documentation Updates**
   - Document common repository patterns and usage guidelines
   - Update service documentation to reflect repository usage
   - Create examples for common repository operations
   - Add detailed API documentation for repository-based endpoints

## Conclusion

The repository layer implementation has made significant progress with 15 of 18 required repositories fully implemented. To complete ADR-014 compliance, focus should be on implementing the three missing repositories, creating the necessary schema factories, and developing comprehensive tests. The successful refactoring of AccountService provides a clear template for the remaining service refactoring work.

Following the recommended priorities will ensure a systematic approach to completing the repository layer refactoring and maintaining high code quality standards throughout the implementation.
