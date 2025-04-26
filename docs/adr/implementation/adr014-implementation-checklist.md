# ADR-014 Implementation Checklist

## Overview

This checklist provides a structured guide for implementing ADR-014 Repository Layer compliance across the Debtonator application. Earlier implementation attempts had significant architectural issues, so this document serves as a definitive implementation guide to ensure all services properly use the repository pattern consistently.

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

## Implementation Checklist

### 1. BaseService Implementation

- [x] Create or update `BaseService` class in `src/services/base.py` with:
  - [x] Repository accessor method with caching
  - [x] Feature flag integration
  - [x] Polymorphic repository support
  - [x] Proper type hints and documentation

```python
class BaseService:
    """Base class for all services with standardized repository initialization."""
    
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        """Initialize base service with session and optional feature flag service."""
        self._session = session
        self._feature_flag_service = feature_flag_service
        self._config_provider = config_provider
        
        # Dictionary to store lazy-loaded repositories
        self._repositories = {}
        
    async def _get_repository(
        self, 
        repository_class: Type,
        polymorphic_type: Optional[str] = None,
        repository_key: Optional[str] = None
    ) -> Any:
        """Get or create a repository instance."""
        # Implementation details...
```

### 2. Repository Factory Refactoring

- [x] Remove non-polymorphic repository methods from `RepositoryFactory`:
  - [x] `create_transaction_history_repository()`
  - [x] `create_cashflow_forecast_repository()`
  - [x] `create_cashflow_metrics_repository()`
  - [x] `create_cashflow_transaction_repository()`
  - [x] `create_realtime_cashflow_repository()`
- [x] Update factory documentation to clarify its refined purpose
- [x] Add explicit guidance that standard repositories should use direct instantiation

### 3. Review and Fix Problematic Implementations

Several services were marked as "complete" but needed review due to problematic implementation:

- [x] Review and fix `cashflow/metrics_service.py`:
  - [x] Check for proper `BaseService` inheritance 
  - [x] Remove any direct `RepositoryFactory` usage for non-polymorphic repositories
  - [x] Ensure feature flag integration through `BaseService`
  - [x] Verify repository methods match service needs

- [x] Review and fix `cashflow/transaction_service.py`:
  - [x] Verify proper repository method usage
  - [x] Check transaction boundaries
  - [x] Ensure consistency with architectural principles

- [x] Review and fix `realtime_cashflow.py`:
  - [x] Refactor to use `BaseService._get_repository()`
  - [x] Remove any direct factory usage for standard repositories
  - [x] Ensure proper feature flag integration

### 4. Service Refactoring

Based on comprehensive review of the codebase, nearly all services need refactoring:

#### Core Services (High Priority)
- [ ] `accounts.py` - Update to properly use `BaseService` pattern
- [ ] `bill_splits.py` - Substantial direct database access
- [ ] `income.py` - Direct database access throughout
- [ ] `recurring_income.py` - No repository pattern implementation
- [ ] `transactions.py` - Review existing implementation and fix issues
- [ ] `payments.py` - Direct database access throughout
- [x] `cashflow/base.py` - Update to properly use `BaseService` pattern

#### Financial Services (Medium Priority)
- [ ] `income_trends.py` - Implement `IncomeTrendsRepository`
- [ ] `balance_history.py` - Direct database access throughout
- [ ] `balance_reconciliation.py` - Direct database access
- [ ] `payment_patterns.py` - Implement `PaymentPatternRepository`
- [ ] `payment_schedules.py` - Implement `PaymentScheduleRepository`
- [ ] `categories.py` - Direct database access throughout
- [ ] `statement_history.py` - Replace direct database access
- [ ] `liabilities.py` - Convert to repository pattern

#### Additional Services (Lower Priority)
- [ ] `bulk_import.py` - Needs repository access implementation
- [ ] `recommendations.py` - Implement `RecommendationRepository`
- [ ] `impact_analysis.py` - Implement `ImpactAnalysisRepository`
- [ ] `income_categories.py` - Implement repository pattern
- [ ] `deposit_schedules.py` - Create repository and refactor service
- [ ] `recurring_bills.py` - Convert to repository pattern
- [ ] `feature_flags.py` - Verify repository usage is correct
- [ ] `factory.py` - Update to align with new repository pattern
- [ ] `system_initialization.py` - Update to use repository pattern

### 5. Repository Implementation

For each non-compliant service, implement the corresponding repository:

#### Core Repositories
- [ ] `AccountRepository` - Review existing implementation
- [ ] `BillSplitRepository` - Create from scratch
- [ ] `IncomeRepository` - Create from scratch
- [ ] `RecurringIncomeRepository` - Create from scratch
- [ ] `TransactionRepository` - Review existing implementation
- [ ] `PaymentRepository` - Create from scratch
- [ ] `PaymentSourceRepository` - Create from scratch

#### Financial Repositories
- [ ] `BalanceHistoryRepository` - Create from scratch
- [ ] `BalanceReconciliationRepository` - Create from scratch
- [ ] `IncomeTrendsRepository` - Create from scratch
- [ ] `CategoryRepository` - Create from scratch
- [ ] `StatementHistoryRepository` - Create from scratch
- [ ] `LiabilityRepository` - Create from scratch
- [ ] `PaymentPatternRepository` - Create from scratch
- [ ] `PaymentScheduleRepository` - Create from scratch

#### Additional Repositories
- [ ] `BulkImportRepository` - Create from scratch
- [ ] `DepositScheduleRepository` - Create from scratch
- [ ] `IncomeCategoryRepository` - Create from scratch
- [ ] `RecommendationRepository` - Create from scratch
- [ ] `ImpactAnalysisRepository` - Create from scratch
- [ ] `RecurringBillRepository` - Create from scratch

Follow this implementation pattern:

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

### 6. Documentation Updates

- [ ] Update `README.md` files in `src/repositories` and `src/services`
- [ ] Update `system_patterns.md` with refined repository pattern
- [ ] Create or update implementation guides for each repository type
- [ ] Document the BaseService usage pattern with examples

## Implementation Guide

### BaseService Implementation

The `BaseService` class is the foundation of our architecture:

1. **Repository Accessor Method**
   ```python
   async def _get_repository(
       self, 
       repository_class: Type,
       polymorphic_type: Optional[str] = None,
       repository_key: Optional[str] = None
   ) -> Any:
       """Get or create a repository instance with caching."""
       
       # Generate cache key from class and optional parameters
       key = f"{repository_class.__name__}"
       if polymorphic_type:
           key += f":{polymorphic_type}"
       if repository_key:
           key += f":{repository_key}"
           
       # Return cached instance if available
       if key in self._repositories:
           return self._repositories[key]
           
       # Create new repository based on type
       if polymorphic_type:
           # Use factory for polymorphic repositories
           if repository_class == AccountRepository:
               repo = await RepositoryFactory.create_account_repository(
                   self._session,
                   account_type=polymorphic_type,
                   feature_flag_service=self._feature_flag_service,
                   config_provider=self._config_provider
               )
           else:
               # Other polymorphic repositories would go here
               raise NotImplementedError(
                   f"Polymorphic repository for {repository_class.__name__} not implemented"
               )
       else:
           # Create standard repository directly
           repo = repository_class(self._session)
           
           # Apply feature flags if available
           if self._feature_flag_service:
               repo = self._wrap_with_feature_flags(repo)
               
       # Cache the repository
       self._repositories[key] = repo
       return repo
   ```

2. **Feature Flag Integration**
   ```python
   def _wrap_with_feature_flags(self, repository: Any) -> Any:
       """Wrap repository with feature flag proxy if available."""
       if not self._feature_flag_service:
           return repository
           
       return FeatureFlagRepositoryProxy(
           repository,
           self._feature_flag_service,
           self._config_provider
       )
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

## Current Status (April 24, 2025)

| Service | Current Status | Required Action |
|---------|-----------------|-----------------|
| `accounts.py` | Partially compliant | Review and refactor to use `BaseService` |
| `feature_flags.py` | Partially compliant | Review and refactor to use `BaseService` |
| `transactions.py` | Implementation issues | Refactor to properly use `BaseService` pattern |
| `cashflow/base.py` | ✅ Fully compliant | Refactored to inherit from app-wide BaseService and use _get_repository |
| `cashflow/metrics_service.py` | ✅ Fully compliant | Updated to use BaseService with proper feature flag integration |
| `cashflow/transaction_service.py` | ✅ Fully compliant | Verified repository pattern usage and updated constructor |
| `realtime_cashflow.py` | ✅ Fully compliant | Refactored to inherit from BaseService and use _get_repository |
| `bill_splits.py` | Not compliant | Major refactoring needed, direct DB access throughout |
| `income.py` | Not compliant | Complete refactoring needed, direct DB access throughout |
| `recurring_income.py` | Not compliant | Complete refactoring needed, no repository pattern |
| `payments.py` | Not compliant | Complete refactoring needed, direct DB access throughout |
| `balance_history.py` | Not compliant | Complete refactoring needed, direct DB access throughout |
| `balance_reconciliation.py` | Not compliant | Complete refactoring needed, direct DB access throughout |
| `categories.py` | Not compliant | Complete refactoring needed, direct DB access throughout |
| `deposit_schedules.py` | Not compliant | Create repository and refactor service |
| `income_trends.py` | Not compliant | Create repository and refactor service |
| `payment_patterns.py` | Not compliant | Create repository and refactor service |
| `payment_schedules.py` | Not compliant | Create repository and refactor service |
| `liabilities.py` | Not compliant | Create repository and refactor service |
| `recommendations.py` | Not compliant | Create repository and refactor service |
| `impact_analysis.py` | Not compliant | Create repository and refactor service |

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

### Repository Implementation Requirements

1. **All repository methods that handle datetimes MUST**:
   - Accept timezone-aware datetimes as input
   - Strip timezone info before database storage
   - Restore timezone info (UTC) after database retrieval
   - Use utility functions for all comparisons

2. **Service refactoring MUST**:
   - Replace all direct datetime and ZoneInfo usage with utility functions
   - Ensure all datetime parameters are properly documented with timezone expectations
   - Use consistent timezone handling patterns throughout

### Validation Step

For each refactored service and repository, verify:

- [ ] No direct imports of `datetime` or `ZoneInfo`
- [ ] All datetime creation uses utility functions
- [ ] Database operations properly handle timezone info
- [ ] All datetime comparisons use utility comparison functions
- [ ] Proper timezone documentation in function signatures

Failure to comply with ADR-011 will cause database queries with datetime filters to behave inconsistently.

## Implementation Patterns and Best Practices

### Common Anti-Patterns Found in Codebase

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

### Repository Method Design

1. **Focus on Business Operations**
   - Design repository methods around business operations, not raw database access
   - Use descriptive method names that reflect domain language
   - Consider what the service needs, not just CRUD operations

2. **Field Filtering and Validation**
   - Handle field filtering and validation consistently
   - Ensure type-specific fields are validated appropriately
   - Preserve optional fields with existing values during updates

3. **Transaction Boundaries**
   - Consider transaction boundaries carefully
   - For multi-step operations, use explicit transaction management
   - Ensure proper rollback in error cases

### Common Pitfalls to Avoid

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
   - INCORRECT: Not passing feature_flag_service to super().__init__
   - CORRECT: `super().__init__(session, feature_flag_service, config_provider)`
