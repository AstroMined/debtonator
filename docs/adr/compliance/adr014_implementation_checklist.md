# ADR-014 Repository Layer Implementation Checklist

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
   - [ ] Add dependencies for remaining repositories

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
   - [ ] Create `src/repositories/income.py`
   - [ ] Implement `IncomeRepository` class
   - [ ] Add income-specific methods:
     - [ ] `get_income_by_source()`
     - [ ] `get_income_in_date_range()`
     - [ ] `get_undeposited_income()`

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
   - [ ] Add `bulk_update()` method
   - [ ] Add transaction boundary support

4. **Relationship Loading**
   - [x] Add support for eager loading with joinedload
   - [ ] Implement selectinload for collections
   - [x] Add options for controlling relationship loading

## Phase 4: Testing

1. **Test Fixtures**
   - [x] Create test database fixtures for repositories
   - [x] Implement repository test fixtures
   - [ ] Implement complete test data generation
   - [ ] Add common test utility functions

2. **Base Repository Tests**
   - [ ] Create `tests/unit/repositories/test_base_repository.py`
   - [ ] Test all CRUD operations
   - [ ] Test filtering and pagination

3. **Model-Specific Repository Tests**
   - [x] Create test file for LiabilityRepository
   - [x] Create test file for PaymentRepository
   - [x] Create test file for PaymentSourceRepository
   - [x] Create test file for BillSplitRepository
   - [ ] Create test files for remaining repositories
   - [ ] Implement comprehensive tests for model-specific methods
   - [ ] Test advanced querying features

4. **Integration Tests**
   - [ ] Create integration tests with real database
   - [ ] Test transaction boundaries
   - [ ] Test complex query scenarios
   - [ ] Test error handling

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
