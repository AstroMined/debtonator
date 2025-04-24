# ADR-014 Compliance: Repository Layer for CRUD Operations

This document tracks compliance with ADR-014, which mandates that all data access in service files must go through the repository layer. Services should not directly access the database or use SQLAlchemy queries but instead use repositories for all CRUD operations.

## Service Files to Review

### Core Services

- [X] src/services/accounts.py
- [X] src/services/balance_history.py
- [X] src/services/balance_reconciliation.py
- [X] src/services/bill_splits.py
- [X] src/services/bulk_import.py
- [X] src/services/categories.py
- [X] src/services/deposit_schedules.py
- [X] src/services/factory.py
- [X] src/services/feature_flags.py
- [X] src/services/impact_analysis.py
- [X] src/services/income_categories.py
- [X] src/services/income_trends.py
- [X] src/services/income.py
- [X] src/services/liabilities.py
- [X] src/services/payment_patterns.py
- [X] src/services/payment_schedules.py
- [X] src/services/payments.py
- [X] src/services/realtime_cashflow.py
- [X] src/services/recommendations.py
- [X] src/services/recurring_bills.py
- [X] src/services/recurring_income.py
- [X] src/services/statement_history.py
- [X] src/services/system_initialization.py
- [X] src/services/transactions.py

### Account Type Services

- [X] src/services/account_types/banking/bnpl.py
- [X] src/services/account_types/banking/checking.py

### Cashflow Services

- [X] src/services/cashflow/base.py
- [X] src/services/cashflow/forecast_service.py
- [X] src/services/cashflow/historical_service.py
- [X] src/services/cashflow/main.py
- [X] src/services/cashflow/metrics_service.py
- [X] src/services/cashflow/transaction_service.py

### Interceptors and Proxies

- [X] src/services/interceptors/feature_flag_interceptor.py
- [X] src/services/proxies/feature_flag_proxy.py

## Compliance Status

### Fully Compliant Files

Files that only use repositories for data access with no direct database queries:

- src/services/accounts.py - Uses proper repository pattern with account_repo, statement_repo, credit_limit_repo, and transaction_repo
- src/services/factory.py - Correctly creates repositories and injects them into services
- src/services/feature_flags.py - Uses repository for all database operations
- src/services/account_types/banking/bnpl.py - Uses RepositoryFactory to create and use repositories
- src/services/account_types/banking/checking.py - No direct database access, proper service pattern
- src/services/cashflow/main.py - Properly delegates to specialized services without direct DB access
- src/services/system_initialization.py - Uses CategoryRepository for initialization operations
- src/services/interceptors/feature_flag_interceptor.py - No direct database access
- src/services/proxies/feature_flag_proxy.py - Proxies service methods without direct database access

### Partially Compliant Files

Files that mostly use repositories but still have some direct database access:
None identified yet

### Non-Compliant Files

Files that primarily use direct database access instead of repositories:

- src/services/deposit_schedules.py - Uses direct SQLAlchemy queries with session instead of repositories
- src/services/income_trends.py - Uses direct database access for queries and analysis
- src/services/transactions.py - Uses direct database operations for all CRUD functions
- src/services/realtime_cashflow.py - Extensive use of direct SQLAlchemy queries and session operations
- src/services/payment_patterns.py - Uses direct database session for all operations
- src/services/payment_schedules.py - Direct database access for CRUD operations
- src/services/recommendations.py - Direct database access with SQLAlchemy queries
- src/services/impact_analysis.py - Extensive direct database access for analysis
- src/services/cashflow/base.py - Contains direct database session usage
- src/services/cashflow/metrics_service.py - Uses direct SQL queries with session.execute and selects

## Required Changes

### High Priority

Key service files that need immediate refactoring to use repositories:

1. src/services/transactions.py:
   - Critical service that directly modifies account balances
   - Used by many other services for core financial tracking
   - Uses direct database access for CRUD operations
   - Should be refactored to use TransactionRepository and AccountRepository

2. src/services/deposit_schedules.py:
   - Important for income tracking and account balance predictions
   - Uses direct session management throughout
   - Should be refactored to use DepositScheduleRepository and IncomeRepository

3. src/services/cashflow/metrics_service.py:
   - Calculates critical financial metrics for the application
   - Currently uses direct database queries for complex operations
   - Should be refactored to use dedicated repositories (LiabilityRepository, AccountRepository)

4. src/services/realtime_cashflow.py:
   - Provides real-time financial data for user decision-making
   - Contains extensive direct database queries
   - Should be refactored to use multiple repositories (AccountRepository, TransactionRepository, etc.)

### Medium Priority

Service files that should be updated but aren't critical paths:

1. src/services/income_trends.py:
   - Used for analysis rather than direct financial operations
   - Contains complex database queries
   - Should be refactored to use IncomeRepository and a specialized IncomeTrendsRepository

2. src/services/cashflow/base.py:
   - Base service with direct session usage
   - Other cashflow services inherit from it
   - Should be refactored to remove direct database access

3. src/services/interceptors/ and src/services/proxies/:
   - Service interceptors and proxies need to be reviewed
   - May contain direct database operations
   - Should be updated to use proper repositories

4. src/services/payment_patterns.py and src/services/payment_schedules.py:
   - Need to be examined for direct database usage
   - Likely contain similar patterns to other services
   - Should be refactored to use appropriate repositories

### Low Priority

Edge cases or rarely used services that can be addressed later:

1. src/services/system_initialization.py:
   - Only used during system startup
   - May contain direct database operations
   - Should be refactored to use appropriate repositories

2. src/services/impact_analysis.py:
   - Used for analysis rather than direct operations
   - Less frequently accessed than core services
   - Should be refactored to use appropriate repositories

3. src/services/recommendations.py:
   - Used for generating user recommendations
   - Not part of core financial functionality
   - Should be refactored to follow repository pattern

## Detailed Violation Analysis

### Additional Service Violations

#### Recurring Income Service Violations

The recurring_income service directly uses SQLAlchemy for all operations:

```python
# Direct database access with query building:
stmt = select(Account).where(Account.id == income_data.account_id)
result = await self.db.execute(stmt)
account = result.unique().scalar_one_or_none()
```

```python
# Direct session management:
self.db.add(recurring_income)
await self.db.commit()
await self.db.refresh(recurring_income)
```

Should be refactored to use repositories:

```python
# Using repositories:
account = await self.account_repository.get(income_data.account_id)
```

```python
# Using repository for creating:
return await self.recurring_income_repository.create(income_data.model_dump())
```

#### Statement History Service Violations

The statement_history service directly uses SQLAlchemy:

```python
# Direct database access:
result = await self.db.execute(select(Account).where(Account.id == account_id))
account = result.scalar_one_or_none()
```

```python
# Direct database manipulation:
self.db.add(statement)
return statement
```

Should be refactored to use repositories:

```python
# Using repositories:
account = await self.account_repository.get(account_id)
```

```python
# Using repository for creation:
return await self.statement_repository.create(statement_data)
```

#### Recurring Bills Service Violations

The recurring_bills service directly uses database operations:

```python
# Direct SQLAlchemy queries:
stmt = select(RecurringBill).options(
    joinedload(RecurringBill.account), joinedload(RecurringBill.liabilities)
)
```

```python
# Direct session management:
self.db.add(db_recurring_bill)
await self.db.commit()
await self.db.refresh(db_recurring_bill)
```

Should be refactored to use repositories:

```python
# Using repositories:
return await self.recurring_bill_repository.get_with_relationships(recurring_bill_id)
```

```python
# Using repository for creation:
return await self.recurring_bill_repository.create(recurring_bill_create.model_dump())
```

#### Balance Reconciliation Service Violations

The balance_reconciliation service directly uses session management:

```python
# Direct session access:
account = await self.session.get(Account, reconciliation_data.account_id)
```

```python
# Direct session manipulation:
self.session.add(reconciliation)
await self.session.commit()
await self.session.refresh(reconciliation)
```

Should be refactored to use repositories:

```python
# Using repositories:
account = await self.account_repository.get(reconciliation_data.account_id)
```

```python
# Using repository for creation:
reconciliation = await self.reconciliation_repository.create(reconciliation_data.model_dump())
```

### Deposit Schedules Service Violations

The deposit_schedules service directly uses SQLAlchemy for all operations:

```python
# Direct database access:
income = await self.session.get(Income, schedule.income_id)
if not income:
    return False, "Income not found", None

# Direct database session management:
self.session.add(db_schedule)
await self.session.commit()
await self.session.refresh(db_schedule)
```

Should be refactored to use repositories:

```python
# Using repositories:
income = await self.income_repository.get(schedule.income_id)

# Using repository for creating:
db_schedule = await self.deposit_schedule_repository.create(schedule.model_dump())
```

### Income Trends Service Violations

The income_trends service directly uses SQLAlchemy:

```python
# Direct database query building:
query = select(Income)
if request.start_date:
    query = query.where(Income.date >= request.start_date)

# Direct database execution:
result = await self.db.execute(query)
income_records = result.scalars().all()
```

Should be refactored to use repositories:

```python
# Using repositories:
income_records = await self.income_repository.get_with_filters(
    start_date=request.start_date,
    end_date=request.end_date,
    source=request.source
)
```

### Transactions Service Violations

The transactions service directly uses database operations:

```python
# Direct account access:
account = await self.session.get(Account, account_id)
if not account:
    raise ValueError(f"Account with id {account_id} not found")

# Direct session manipulation:
self.session.add(transaction)
await self.session.commit()
await self.session.refresh(transaction)
```

Should be refactored to use repositories:

```python
# Using repositories:
account = await self.account_repository.get(account_id)

# Repository creation:
transaction = await self.transaction_repository.create({
    "account_id": account_id,
    "amount": transaction_data.amount,
    "transaction_type": transaction_data.transaction_type,
    "description": transaction_data.description,
    "transaction_date": transaction_data.transaction_date,
})
```

### Realtime Cashflow Service Violations

The realtime_cashflow service extensively uses direct database access:

```python
# Direct query building:
query = select(Account)
result = await self.db.execute(query)
accounts = result.scalars().all()

# Complex direct query operations:
transfers_query = (
    select(PaymentSource)
    .join(Payment, PaymentSource.payment_id == Payment.id)
    .where(
        and_(
            PaymentSource.account_id.in_([acc1.id, acc2.id]),
            Payment.category == "Transfer",
        )
    )
)
```

Should be refactored to use repositories:

```python
# Using repositories:
accounts = await self.account_repository.get_all()

# Using specialized repository methods:
transfers = await self.payment_source_repository.get_transfers_between_accounts(
    account_ids=[acc1.id, acc2.id]
)
```

### Cashflow Metrics Service Violations

The cashflow/metrics_service directly uses SQLAlchemy:

```python
# Direct query building:
accounts_query = select(Account)
accounts = (await self.db.execute(accounts_query)).scalars().all()

# Complex direct database access:
result = await self.db.execute(
    select(Liability)
    .outerjoin(Payment)
    .where(
        Liability.primary_account_id == account_id,
        Liability.due_date >= start_date,
        Liability.due_date <= end_date,
        Payment.id == None,  # No associated payments
    )
)
```

Should be refactored to use repositories:

```python
# Using repositories:
accounts = await self.account_repository.get_all()

# Using specialized repository methods:
liabilities = await self.liability_repository.get_unpaid_in_date_range(
    account_id=account_id,
    start_date=start_date,
    end_date=end_date
)
```

## Summary of Findings

After a complete examination of all service files in the project, I've identified the following compliance status:

1. **Fully Compliant Services (7 services)**:  
   - accounts.py
   - feature_flags.py
   - account_types/banking/bnpl.py
   - account_types/banking/checking.py
   - system_initialization.py
   - interceptors/feature_flag_interceptor.py
   - proxies/feature_flag_proxy.py
   - cashflow/main.py

2. **Non-Compliant Services (10 services)**:  
   - deposit_schedules.py
   - income_trends.py
   - payment_patterns.py
   - payment_schedules.py
   - recommendations.py
   - impact_analysis.py
   - transactions.py
   - realtime_cashflow.py
   - cashflow/base.py
   - cashflow/metrics_service.py

3. **Required Repositories**:  
   To achieve full compliance, the following new repositories need to be implemented:
   - DepositScheduleRepository
   - IncomeTrendsRepository
   - PaymentPatternRepository
   - PaymentScheduleRepository
   - RecommendationRepository
   - ImpactAnalysisRepository
   - TransactionRepository
   - RealtimeCashflowRepository
   - CashflowRepository
   - CashflowMetricsRepository

4. **Common Patterns in Non-Compliant Services**:
   - Direct use of session.execute() with SQLAlchemy selects
   - Direct entity creation with session.add() and commit()
   - Complex queries with joins and relationships
   - Direct ORM object manipulation
   - Lack of clear service-repository separation

## Implementation Plan

1. **Create Missing Repositories**
   - Implement these repositories in priority order:
     - TransactionRepository
     - CashflowRepository and CashflowMetricsRepository
     - RealtimeCashflowRepository
     - DepositScheduleRepository
     - PaymentPatternRepository and PaymentScheduleRepository
     - ImpactAnalysisRepository
     - RecommendationRepository
     - IncomeTrendsRepository

2. **Implement Repository Features**
   - Ensure each repository implements:
     - Core CRUD operations (get, create, update, delete)
     - Specialized query methods needed by each service
     - Proper relationship handling methods
     - Appropriate transaction boundaries

3. **Refactor Services in Priority Order**
   - Phase 1: High Priority Services (1-2 months)
     - transactions.py
     - deposit_schedules.py
     - cashflow/metrics_service.py
     - realtime_cashflow.py
   - Phase 2: Medium Priority Services (1-2 months)
     - income_trends.py
     - cashflow/base.py
     - payment_patterns.py and payment_schedules.py
   - Phase 3: Low Priority Services (1-2 months)
     - recommendations.py
     - impact_analysis.py
     - Any remaining services

4. **Testing Strategy**
   - Implement comprehensive integration tests for each repository
   - Create tests for service-repository interactions
   - Test transaction boundaries for correctness
   - Create regression tests to ensure functionality is preserved

5. **Documentation Updates**
   - Update service documentation to describe repository dependencies
   - Create repository method documentation
   - Update README.md files for repositories directory
   - Add examples of proper service-repository interactions

## Progress Tracking

| Service | Repository Needed | Status | Notes |
|---------|-------------------|--------|-------|
| accounts.py | AccountRepository | ✅ Complete | Using repositories properly |
| feature_flags.py | FeatureFlagRepository | ✅ Complete | Using repositories properly |
| account_types/banking/bnpl.py | AccountRepository | ✅ Complete | Using RepositoryFactory |
| account_types/banking/checking.py | AccountRepository | ✅ Complete | No direct DB access |
| system_initialization.py | CategoryRepository | ✅ Complete | Using repositories properly |
| interceptors/feature_flag_interceptor.py | N/A | ✅ Complete | No direct DB access needed |
| proxies/feature_flag_proxy.py | N/A | ✅ Complete | No direct DB access needed |
| deposit_schedules.py | DepositScheduleRepository | ❌ Not Started | Uses direct session management |
| income_trends.py | IncomeTrendsRepository | ❌ Not Started | Direct database queries |
| payment_patterns.py | PaymentPatternRepository | ❌ Not Started | Direct database operations |
| payment_schedules.py | PaymentScheduleRepository | ❌ Not Started | Direct database operations |
| recommendations.py | RecommendationRepository | ❌ Not Started | Direct database queries |
| impact_analysis.py | ImpactAnalysisRepository | ❌ Not Started | Extensive direct DB usage |
| transactions.py | TransactionRepository | ❌ Not Started | Direct database operations |
| realtime_cashflow.py | RealtimeCashflowRepository | ❌ Not Started | Extensive direct DB usage |
| cashflow/base.py | CashflowRepository | ❌ Not Started | Direct session usage |
| cashflow/metrics_service.py | CashflowMetricsRepository | ❌ Not Started | Direct database operations |

## Considerations During Refactoring

1. **Transaction Boundaries**: Ensure proper transaction handling during the transition
2. **Dependency Injection**: Update the factory.py file to include all new repositories
3. **Repository Method Design**:
   - Design repository methods to support all service use cases
   - Consider specialized methods for complex queries
   - Ensure repositories follow the polymorphic pattern where appropriate
4. **Testing**:
   - Implement integration tests for each repository
   - Ensure service functionality remains identical after refactoring
5. **Documentation**:
   - Update service documentation to reflect repository dependencies
   - Create comprehensive repository method documentation
6. **Factory Updates**:
   - Update or create factory methods for all repositories
   - Update service factories to inject repositories

## Progress

- [X] Initial assessment complete
- [X] Comprehensive service review (ALL services examined)
- [ ] High priority files refactored
- [ ] Medium priority files refactored
- [ ] Low priority files refactored
- [ ] All service files compliant with ADR-014
