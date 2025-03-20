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

3. **Model-Specific Repository Tests**
   - [x] Create test file for LiabilityRepository
   - [x] Create test file for PaymentRepository
   - [x] Create test file for PaymentSourceRepository
   - [x] Create test file for BillSplitRepository
   - [x] Create test file for RecurringBillRepository
   - [x] Create test file for StatementHistoryRepository
   - [x] Create test file for BalanceHistoryRepository
   - [x] Create test file for CategoryRepository
   - [x] Create test file for CreditLimitHistoryRepository
   - [x] Create test file for BalanceReconciliationRepository
   - [x] Create test file for TransactionHistoryRepository
   - [x] Implement comprehensive tests for model-specific methods
   - [x] Test advanced querying features

4. **Integration Tests**
   - [x] Create integration tests with real database
   - [x] Test transaction boundaries
   - [x] Test complex query scenarios
   - [x] Test error handling

## Phase 5: Service Refactoring

1. **Account Service Refactoring**
   - [ ] Update `src/services/accounts.py` to use repositories
   - [ ] Update service tests
   - [ ] Validate refactored approach

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

1. **Create the Foundation First**
   - Implement the base repository layer
   - Create repository factory
   - Set up dependency injection
   - Write thorough tests for the base repository

2. **Build Key Repositories Incrementally**
   - Start with Account repository as it's fundamental
   - Implement Bill repository next (related to core functionality)
   - Add Payment and BillSplit repositories (core financial operations)
   - Implement remaining repositories

3. **Test Each Repository Thoroughly**
   - Create unit tests for specific repository features
   - Develop integration tests with real database fixtures
   - Test transaction boundaries and error handling
   - Verify advanced querying capabilities

4. **Refactor One Service as Proof-of-Concept**
   - Choose a single service (Account service is recommended)
   - Refactor to use repositories
   - Validate approach with comprehensive tests
   - Document lessons learned for other service refactorings

5. **Gradually Refactor Remaining Services**
   - Use a consistent pattern based on the proof-of-concept
   - Update each service individually
   - Maintain thorough test coverage during refactoring
