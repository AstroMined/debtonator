# ADR-014 Implementation Checklist

## Overview

This checklist provides a structured guide for implementing ADR-014 Repository Layer compliance across the Debtonator application. Earlier implementation attempts had significant architectural issues, so this document serves as a definitive implementation guide to ensure all services properly use the repository pattern consistently.

To make this work more manageable, the implementation has been divided into focused phases, each designed to be completed in a single coding session. This approach prevents scope creep and ensures steady progress.

## Core Architectural Principles

### Repository Types Classification

1. **Polymorphic Repositories**
   - Extend `PolymorphicBaseRepository`
   - Used for entities with polymorphic relationships (e.g., accounts)
   - Accessed through `BaseService._get_repository()` with `polymorphic_type` parameter
   - Require type-specific handling via discriminator field

2. **Standard Repositories**
   - Extend `BaseRepository`
   - Used for standard entities without polymorphic relationships
   - Accessed directly through `BaseService._get_repository()`
   - No type-specific handling needed

### Service Layer Integration

1. **BaseService Implementation**
   - All services must inherit from `BaseService`
   - Use `_get_repository()` method for standardized repository access
   - Implement lazy loading and caching of repositories
   - Ensure automatic feature flag integration

2. **Repository Factory Focus**
   - `RepositoryFactory` should be used **ONLY** for polymorphic repositories
   - Remove all non-polymorphic repository factory methods
   - Keep only `create_account_repository()` and similar polymorphic entity methods
   - Let `BaseService` handle standard repository instantiation

## Implementation Phases

### Completed Work

- [x] **Phase 0: Foundation (COMPLETED)**
  - [x] Created `BaseService` class in `src/services/base.py`
  - [x] Refined Repository Factory to focus solely on polymorphic repositories
  - [x] Fixed cashflow services to properly use the repository pattern:
    - [x] Refactored cashflow/base.py to properly inherit from app-wide BaseService
    - [x] Updated metrics_service.py with proper feature flag integration
    - [x] Refactored transaction_service.py with proper inheritance
    - [x] Updated realtime_cashflow.py to follow the correct architectural pattern

### Core Implementation Phases (Remaining)

Each phase is designed to be completed in a single coding session:

#### Core Account-Related Services (High Priority)

**Focus**: Refactor account-related services to follow the repository pattern

- [x] **Phase 1: Account Service Refactoring** ✅
  - [x] Review and refactor `accounts.py` to use `BaseService` pattern
  - [x] Apply consistent repository access through _get_repository
  - [x] Handle polymorphic repository access properly
  - [x] Update feature flag access to use protected attribute
  - [x] Completion criteria: Successful implementation of repository pattern

- [x] **Phase 2: Transaction Service Refactoring** ✅
  - [x] Review and refactor `transactions.py` to use `BaseService` pattern properly
  - [x] Replace direct property-based repository access with _get_repository calls
  - [x] Verify proper datetime handling in repository methods
  - [x] Remove unused imports and fix code quality issues
  - [x] Completion criteria: Successful implementation of repository pattern

- [x] **Phase 3: Bill Splits Service Refactoring** ✅
  - [x] Create dedicated `BillSplitRepository` with appropriate methods
  - [x] Refactor `bill_splits.py` service to use repository pattern
  - [x] Move direct DB access to repository methods
  - [x] Ensure proper transaction boundary handling
  - [x] Completion criteria: Bill splits functionality working correctly with repository pattern

#### Income-Related Services (High Priority)

**Focus**: Refactor income-related services to follow the repository pattern

- [x] **Phase 4: Income Service Refactoring** ✅
  - [x] Discovered the `IncomeRepository` already exists with comprehensive methods
  - [x] Refactored `income.py` service to inherit from `BaseService`
  - [x] Replaced all direct DB access with repository method calls
  - [x] Ensured proper transaction boundary handling
  - [x] Maintained feature flag integration with proper constructor
  - [x] Completion criteria: Income service using repository pattern exclusively

- [x] **Phase 5: Recurring Income Service Refactoring** ✅
  - [x] Used existing `RecurringIncomeRepository` that was already implemented
  - [x] Refactored `recurring_income.py` service to inherit from BaseService
  - [x] Replaced all direct database queries with repository method calls
  - [x] Added find_by_recurring_and_date method to IncomeRepository
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Completion criteria: Recurring income service using repository pattern exclusively

- [x] **Phase 6: Payment Service Refactoring** ✅ COMPLETED
  - [x] Used existing `PaymentRepository` and `PaymentSourceRepository` implementations
  - [x] Refactored `payments.py` service to inherit from BaseService
  - [x] Replaced all direct database queries with repository method calls
  - [x] Updated validation methods to use repositories for account and reference verification
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Completion criteria: Payment service using repository pattern exclusively

#### Financial Analysis Services (Medium Priority)

**Focus**: Refactor financial analysis services to follow the repository pattern

- [x] **Phase 7: Income Trends Implementation** ✅ COMPLETED
  - [x] Create `IncomeTrendsRepository` with appropriate methods
  - [x] Refactor `income_trends.py` to use repository pattern
  - [x] Move specialized analysis queries to repository methods
  - [x] Completion criteria: Income trends service using repository pattern exclusively

- [x] **Phase 8: Payment Patterns Implementation** ✅ COMPLETED
  - [x] Created `PaymentPatternRepository` with appropriate methods
  - [x] Refactored `payment_patterns.py` to use repository pattern
  - [x] Moved specialized pattern analysis to repository methods
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Implemented service delegation to repository for data access
  - [x] Completion criteria: Payment patterns service using repository pattern exclusively

- [x] **Phase 9: Payment Schedules Implementation** ✅ COMPLETED
  - [x] Used existing `PaymentScheduleRepository` with comprehensive methods
  - [x] Refactored `payment_schedules.py` to inherit from BaseService
  - [x] Replaced direct database queries with repository method calls
  - [x] Properly initialized PaymentService with all dependencies
  - [x] Applied ADR-011 datetime compliance with utility functions
  - [x] Added new methods leveraging specialized repository functions
  - [x] Completion criteria: Payment schedules service using repository pattern exclusively

#### Balance Management Services (Medium Priority)

**Focus**: Refactor balance-related services to follow the repository pattern

- [x] **Phase 10: Balance History Implementation** ✅ COMPLETED
  - [x] Used existing `BalanceHistoryRepository` with comprehensive methods
  - [x] Refactored `balance_history.py` to inherit from BaseService
  - [x] Replaced direct database queries with repository method calls
  - [x] Applied ADR-011 datetime compliance with utility functions
  - [x] Added new methods leveraging specialized repository functions
  - [x] Implemented proper feature flag integration
  - [x] Completion criteria: Balance history service using repository pattern exclusively

- [x] **Phase 11: Balance Reconciliation Implementation** ✅ COMPLETED
  - [x] Used existing `BalanceReconciliationRepository` with appropriate methods
  - [x] Refactored `balance_reconciliation.py` to use repository pattern
  - [x] Properly initialized service to inherit from BaseService
  - [x] Used _get_repository method for standardized repository access
  - [x] Replaced all direct database queries with repository method calls
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Added enhanced repository methods for comprehensive auditing and analysis
  - [x] Completion criteria: Balance reconciliation service using repository pattern exclusively

- [x] **Phase 12: Categories Implementation** ✅ COMPLETED
  - [x] Used existing `CategoryRepository` with specialized methods
  - [x] Refactored `categories.py` to use repository pattern
  - [x] Properly initialized service to inherit from BaseService
  - [x] Used _get_repository method for standardized repository access
  - [x] Replaced all direct database queries with repository method calls
  - [x] Leveraged proper system category protection in the repository
  - [x] Maintained specialized category tree composition methods
  - [x] Added support for additional repository methods
  - [x] Completion criteria: Categories service using repository pattern exclusively

#### Statement and Liability Services (Medium Priority)

**Focus**: Refactor statement and liability-related services to follow the repository pattern

- [x] **Phase 13: Statement History Implementation** ✅ COMPLETED
  - [x] Reviewed existing StatementHistoryRepository implementation
  - [x] Refactored StatementService to inherit from BaseService
  - [x] Updated constructor to properly initialize BaseService
  - [x] Used _get_repository method for standardized repository access
  - [x] Replaced direct database access with repository method calls
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Added support for additional methods from repository
  - [x] Enhanced method documentation with comprehensive docstrings
  - [x] Completion criteria: Statement history service using repository pattern exclusively

- [x] **Phase 14: Liabilities Implementation** ✅ COMPLETED
  - [x] Used existing LiabilityRepository with comprehensive methods
  - [x] Refactored LiabilityService to inherit from BaseService
  - [x] Updated constructor to properly initialize BaseService
  - [x] Used _get_repository method for standardized repository access
  - [x] Replaced direct database access with repository method calls
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Updated validation methods to use repositories for account and category verification
  - [x] Added support for additional methods from repository
  - [x] Enhanced error handling with proper validation
  - [x] Maintained feature flag integration with protected attribute
  - [x] Completion criteria: Liabilities service using repository pattern exclusively

#### Supporting Services (Lower Priority)

**Focus**: Refactor supporting services to follow the repository pattern

- [x] **Phase 15: Bulk Import Implementation** ✅ COMPLETED
  - [x] Refactored BulkImportService to inherit from BaseService
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Improved schema organization by creating dedicated schema file
  - [x] Enhanced documentation with comprehensive docstrings
  - [x] Maintained service orchestration pattern through other services
  - [x] Completion criteria: BulkImport service properly using repository pattern

- [x] **Phase 16: Deposit Schedules Implementation** ✅ COMPLETED
  - [x] Used existing DepositScheduleRepository with comprehensive methods
  - [x] Refactored DepositScheduleService to inherit from BaseService
  - [x] Replaced all direct database queries with repository method calls
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Enhanced service methods to use repository pattern consistently
  - [x] Added improved documentation and error handling
  - [x] Completion criteria: Deposit schedules service using repository pattern exclusively

- [x] **Phase 17: System Services Implementation** ✅ COMPLETED
  - [x] Refactored `feature_flags.py` to properly use repository pattern
  - [x] Updated `system_initialization.py` to use repository pattern consistently
  - [x] Ensured proper feature flag integration and initialization
  - [x] Added system feature flags initialization during system startup
  - [x] Maintained backward compatibility for existing code
  - [x] Completion criteria: System services using repository pattern exclusively

#### Analysis and Recommendation Services (Lower Priority)

**Focus**: Refactor analysis and recommendation services to follow the repository pattern

- [ ] **Phase 18: Recommendations Implementation**
  - [x] Refactor RecommendationService to use repository pattern
  - [x] Leverage existing repositories instead of creating new ones
  - [x] Replace direct database access with repository method calls
  - [x] Use specialized MetricsService instead of general CashflowService
  - [x] Apply proper ADR-011 datetime compliance with utility functions
  - [x] Enhance error handling with descriptive return values
  - [x] Add comprehensive documentation with method docstrings
  - [x] Update reference to account attributes (account_type, credit_limit)
  - [x] Completion criteria: Recommendations service using repository pattern exclusively

- [ ] **Phase 19: Impact Analysis Implementation**
  - [x] Refactor ImpactAnalysisService to inherit from BaseService
  - [x] Replace direct database queries with repository methods
  - [x] Use existing repositories (LiabilityRepository, AccountRepository)
  - [x] Ensure proper ADR-011 datetime compliance
  - [x] Update reference to account attributes (account_type, credit_limit)
  - [x] Add comprehensive documentation with method docstrings
  - [x] Enhanced error handling with descriptive error messages
  - [x] Completion criteria: Impact analysis service using repository pattern exclusively

- [ ] **Phase 20: Recurring Bills Implementation**
  - [x] Used existing RecurringBillRepository with appropriate methods
  - [x] Refactored RecurringBillService to inherit from BaseService
  - [x] Replaced all direct database queries with repository method calls
  - [x] Applied proper ADR-011 datetime compliance with utility functions
  - [x] Enhanced error handling with appropriate validation
  - [x] Added comprehensive method docstrings
  - [x] Updated implementation to use _get_repository method consistently
  - [x] Completion criteria: Recurring bills service using repository pattern exclusively

#### Documentation and Validation

**Focus**: Complete and validate the repository pattern implementation across the application

- [ ] **Phase 21: README and Documentation Updates**
  - [ ] Update `README.md` files in `src/repositories` and `src/services`
  - [ ] Update `system_patterns.md` with refined repository pattern
  - [ ] Completion criteria: All documentation updated to reflect the new architecture

- [ ] **Phase 22: Cross-Application Testing and Validation**
  - [ ] Run full test suite to verify application integrity
  - [ ] Verify all services follow the repository pattern
  - [ ] Check for any remaining direct database access
  - [ ] Completion criteria: All tests passing with no architectural violations

- [ ] **Phase 23: Final Review and Performance Analysis**
  - [ ] Review repository method usage patterns
  - [ ] Identify and fix any performance bottlenecks
  - [ ] Ensure proper transaction boundaries
  - [ ] Completion criteria: Application performing optimally with the repository pattern

## Implementation Guide

### Repository Implementation Pattern

When creating a new repository, follow this pattern:

```python
class SomeRepository(BaseRepository[ModelType, int]):
    """Repository for some operations."""
    
    def __init__(self, session: AsyncSession):
        model_class = SomeModel
        super().__init__(session, model_class)
    
    async def some_specialized_method(self, param: Any) -> List[ModelType]:
        """Specialized query method."""
        stmt = select(self.model_class).where(
            self.model_class.some_field == param
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

### Service Refactoring Pattern

When refactoring services, follow this pattern:

```python
class SomeService(BaseService):
    """Service for some domain operations."""
    
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        super().__init__(session, feature_flag_service, config_provider)
        
    async def some_operation(self) -> Result:
        # Get standard repository 
        repo = await self._get_repository(SomeRepository)
        
        # Use repository methods
        result = await repo.some_method()
        return result
        
    async def account_specific_operation(self, account_type: str) -> Result:
        # Get polymorphic repository with type
        account_repo = await self._get_repository(
            AccountRepository, 
            polymorphic_type=account_type
        )
        
        # Use repository methods
        result = await account_repo.some_method()
        return result
```

## Testing Guidelines

For each refactoring phase, ensure:

1. **Repository Testing**
   - Test all repository methods with a real test database
   - Include edge cases (empty results, NULL values)
   - Test transaction boundaries for multi-operation methods
   - Verify proper error handling and validation

2. **Service Testing**
   - Test services with real repositories (no mocks)
   - Verify proper inheritance from `BaseService`
   - Test proper feature flag integration
   - Ensure identical functionality after refactoring

## Validation Checklist

For each refactored service, verify:

- [ ] Service inherits from `BaseService`
- [ ] No direct database access (SQLAlchemy queries)
- [ ] All repositories accessed through `_get_repository`
- [ ] All specialized database operations moved to repositories
- [ ] Proper error handling and validation
- [ ] Feature flag integration maintained
- [ ] Tests pass without modifications
- [ ] Documentation updated

## Current Status (April 26, 2025)

| Service | Current Status | Required Action | Phase |
|---------|----------------|-----------------|-------|
| `cashflow/base.py` | ✅ Fully compliant | None needed | 0 |
| `cashflow/metrics_service.py` | ✅ Fully compliant | None needed | 0 |
| `cashflow/transaction_service.py` | ✅ Fully compliant | None needed | 0 |
| `realtime_cashflow.py` | ✅ Fully compliant | None needed | 0 |
| `accounts.py` | ✅ Fully compliant | None needed | 1 |
| `transactions.py` | ✅ Fully compliant | None needed | 2 |
| `bill_splits.py` | ✅ Fully compliant | None needed | 3 |
| `income.py` | ✅ Fully compliant | None needed | 4 |
| `recurring_income.py` | ✅ Fully compliant | None needed | 5 |
| `payments.py` | ✅ Fully compliant | None needed | 6 |
| `income_trends.py` | ✅ Fully compliant | None needed | 7 |
| `payment_patterns.py` | ✅ Fully compliant | None needed | 8 |
| `payment_schedules.py` | ✅ Fully compliant | None needed | 9 |
| `balance_history.py` | ✅ Fully compliant | None needed | 10 |
| `balance_reconciliation.py` | ✅ Fully compliant | None needed | 11 |
| `categories.py` | ✅ Fully compliant | None needed | 12 |
| `statement_history.py` | ✅ Fully compliant | None needed | 13 |
| `liabilities.py` | ✅ Fully compliant | None needed | 14 |
| `bulk_import.py` | ✅ Fully compliant | None needed | 15 |
| `deposit_schedules.py` | ✅ Fully compliant | None needed | 16 |
| `feature_flags.py` | ✅ Fully compliant | None needed | 17 |
| `system_initialization.py` | ✅ Fully compliant | None needed | 17 |
| `recommendations.py` | ✅ Fully compliant | None needed | 18 |
| `impact_analysis.py` | ✅ Fully compliant | None needed | 19 |
| `recurring_bills.py` | ✅ Fully compliant | None needed | 20 |
| `income_categories.py` | Not compliant | Implement repository pattern | 20 |
| `factory.py` | Not compliant | Update to align with new repository pattern | 17 |

## ADR-011 Datetime Compliance Requirements

When implementing repositories and refactoring services, all datetime operations **MUST** use the utility functions from `src/utils/datetime_utils.py` module. Direct usage of `datetime` module or `ZoneInfo` is strictly prohibited.

### Key Datetime Utility Functions

1. **UTC Handling**
   - `ensure_utc(dt)` - Guarantees timezone awareness for datetime objects
   - `naive_utc_from_date(year, month, day)` - Creates naive UTC datetime from date components
   - `utc_now()` - Gets current UTC time (timezone-aware)
   - `strip_tzinfo(dt)` - Removes timezone info for database storage

2. **Database Operations**
   - All datetimes stored in the database MUST be naive (no timezone)
   - Use `strip_tzinfo(dt)` before storing in the database
   - Use `ensure_utc(dt)` after retrieving from the database

3. **Comparisons and Validation**
   - `datetime_equals(dt1, dt2, ignore_timezone=True)` - For equality comparisons
   - `datetime_greater_than(dt1, dt2, ignore_timezone=True)` - For ordering comparisons
   - Never compare naive and aware datetimes directly

### Common Anti-Patterns to Avoid

```python
# ANTI-PATTERN: Direct datetime usage
from datetime import datetime
current_time = datetime.now()  # Wrong: Uses system timezone, not UTC

# ANTI-PATTERN: Direct ZoneInfo usage
from zoneinfo import ZoneInfo
dt = datetime.now(ZoneInfo("UTC"))  # Wrong: Direct ZoneInfo import

# ANTI-PATTERN: Naive comparison
if db_datetime == user_datetime:  # Wrong: Might compare naive to aware

# CORRECT PATTERN: Using utility functions
from src.utils.datetime_utils import utc_now, ensure_utc, datetime_equals
current_time = utc_now()  # Right: Uses utility function
converted_dt = ensure_utc(user_input_dt)  # Right: Ensures timezone awareness
if datetime_equals(db_dt, user_dt, ignore_timezone=True):  # Right: Safe comparison
```

### Implementation Patterns and Best Practices

#### Common Anti-Patterns Found in Codebase

1. **Direct Database Access**

   ```python
   # ANTI-PATTERN: Direct database session usage
   result = await self.db.execute(select(Model).where(Model.field == value))
   item = result.scalar_one_or_none()
   
   # CORRECT PATTERN: Repository usage
   repo = await self._get_repository(ModelRepository)
   item = await repo.get_by_field(field, value)
   ```

2. **Session Manipulation in Services**

   ```python
   # ANTI-PATTERN: Session management in services
   self.db.add(new_entity)
   await self.db.commit()
   await self.db.refresh(new_entity)
   
   # CORRECT PATTERN: Repository handles session management
   repo = await self._get_repository(ModelRepository)
   new_entity = await repo.create(entity_data)
   ```

3. **Mixed Business Logic and Data Access**

   ```python
   # ANTI-PATTERN: Business logic mixed with data access
   async def process_payment(self, payment_data):
       stmt = select(Account).where(Account.id == payment_data.account_id)
       result = await self.db.execute(stmt)
       account = result.scalar_one_or_none()
       
       # Business logic directly using DB objects
       if account.available_balance < payment_data.amount:
           raise ValueError("Insufficient funds")
           
       # More direct DB operations...
   
   # CORRECT PATTERN: Separation of concerns
   async def process_payment(self, payment_data):
       # Get repositories
       account_repo = await self._get_repository(AccountRepository)
       payment_repo = await self._get_repository(PaymentRepository)
       
       # Use repository methods
       account = await account_repo.get(payment_data.account_id)
       
       # Business logic in service
       if account.available_balance < payment_data.amount:
           raise ValueError("Insufficient funds")
           
       # Repository handles data operations
       payment = await payment_repo.create(payment_data)
       return payment
   ```

#### Common Pitfalls to Avoid

1. **Direct Repository Factory Usage for Standard Repositories**
   - INCORRECT: `repo = await RepositoryFactory.create_some_repository(session)`
   - CORRECT: `repo = await self._get_repository(SomeRepository)`

2. **Missing BaseService Inheritance**
   - INCORRECT: `class SomeService: ...`
   - CORRECT: `class SomeService(BaseService): ...`

3. **Direct Database Access**
   - INCORRECT: `result = await self._session.execute(select(Model))`
   - CORRECT: `result = await repo.get_by_criteria(criteria)`

4. **Missing Feature Flag Integration**
   - INCORRECT: Not passing feature_flag_service to `super().__init__`
   - CORRECT: `super().__init__(session, feature_flag_service, config_provider)`
