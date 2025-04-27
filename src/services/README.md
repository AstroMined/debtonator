# Services Layer

## Purpose

The services layer is the heart of Debtonator's business logic, orchestrating operations between the API layer and repositories. Services encapsulate domain-specific operations, enforce business rules, and coordinate multi-entity workflows.

## Related Documentation

- [Repository Layer README](/code/debtonator/src/repositories/README.md)
- [ADR-014: Repository Layer for CRUD Operations](/code/debtonator/docs/adr/backend/014-repository-layer-for-crud-operations.md)
- [ADR-011: Datetime Standardization](/code/debtonator/docs/adr/backend/011-datetime-standardization.md)
- [UTC Datetime Compliance Guide](/code/debtonator/docs/guides/utc_datetime_compliance.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md)

## Architecture

The services layer:

1. **Consumes repositories**: All data access must occur through repositories
2. **Enforces business rules**: Validation logic not appropriate for schemas or models
3. **Orchestrates workflows**: Manages multi-step business processes
4. **Handles transactions**: Ensures data integrity across multiple operations
5. **Implements feature flags**: Services are wrapped by feature flag proxies
6. **Enforces datetime standards**: Uses datetime_utils.py for all datetime operations

```tree
src/services/
├── factory.py                # Service factory with dependency injection
├── accounts.py               # Core account operations and validation
├── payments.py               # Payment processing logic
├── feature_flags.py          # Feature flag management
├── account_types/            # Type-specific service operations
│   ├── banking/
│   │   ├── checking.py
│   │   ├── credit.py
│   │   └── ...
├── cashflow/                 # Cashflow-specific services
│   ├── cashflow_base.py      # Base service for all cashflow services
│   ├── cashflow_forecast_service.py   # Forecast generation
│   ├── cashflow_historical_service.py # Historical analysis
│   ├── cashflow_metrics_service.py    # Financial metrics calculations
│   └── cashflow_transaction_service.py # Transaction management
├── interceptors/             # Service method interceptors
│   └── feature_flag_interceptor.py
└── proxies/                  # Service method proxies
    └── feature_flag_proxy.py
```

## Implementation Patterns

### Repository Usage Pattern

All services should inherit from BaseService and use its repository access methods:

```python
class SomeService(BaseService):
    """Service for some domain operations."""
    
    async def some_operation(self) -> Result:
        # Get repository instance using BaseService._get_repository
        repo = await self._get_repository(SomeRepository)
        
        # Use repository methods
        return await repo.some_method()
        
    async def account_specific_operation(self, account_type: str) -> Result:
        # Get polymorphic repository with specific type
        account_repo = await self._get_repository(
            AccountRepository, 
            polymorphic_type=account_type
        )
        
        # Use repository methods
        return await account_repo.some_method()
```

### Datetime Handling Pattern

All services must use the utilities from `datetime_utils.py` for datetime operations:

```python
from src.utils.datetime_utils import (
    ensure_utc, utc_now, days_from_now, 
    naive_start_of_day, naive_end_of_day
)

class SomeService(BaseService):
    """Service with proper datetime handling."""
    
    async def get_data_for_date_range(self, start_date, end_date):
        # Ensure UTC timezone for business logic
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)
        
        # Get repository
        repo = await self._get_repository(SomeRepository)
        
        # For database operations, use naive datetime functions
        db_start = naive_start_of_day(start_date)
        db_end = naive_end_of_day(end_date)
        
        # Use repository methods with proper date parameters
        return await repo.get_by_date_range(db_start, db_end)
```

### Transaction Management

Services handle transaction boundaries across multiple repositories:

```python
async def create_bill_with_splits(
    self, 
    bill_data: LiabilityCreate, 
    splits: List[BillSplitCreate]
) -> Liability:
    # Create the bill
    bill = await self.liability_repository.create(bill_data.model_dump())
    
    try:
        # Create the splits
        for split in splits:
            split_data = split.model_dump()
            split_data["liability_id"] = bill.id
            await self.bill_split_repository.create(split_data)
        
        # Everything succeeded
        return bill
    except Exception as e:
        # Rollback (handled by repository's session)
        raise ValueError(f"Failed to create bill splits: {str(e)}")
```

### BaseService Pattern

Services inherit from the BaseService class for standardized repository initialization:

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

The BaseService class provides several key benefits:

- Lazy loading: Repositories are created only when needed
- Caching: Repositories are created once and reused
- Automatic feature flag integration
- Consistent initialization across all services

### Feature Flag Integration

Services are wrapped by proxies to enforce feature flags:

```python
# Service method intercepted by feature flag proxy
try:
    # This will be intercepted before execution to check feature flags
    result = await account_service.create_account(account_data)
except FeatureDisabledError as e:
    # Handle the disabled feature
    raise HTTPException(status_code=403, detail=str(e))
```

## Key Responsibilities

1. **Domain Logic**: Core business rules and operations
2. **Multi-Entity Coordination**: Operations involving multiple repositories
3. **Transaction Management**: Ensuring data consistency across operations
4. **Validation Logic**: Complex validation beyond schema-level checks
5. **Feature Enforcement**: Ensuring features are properly gated

## Testing Strategy

1. **Integration Testing**: Most service tests should be integration tests
2. **Real Objects**: Use real repositories with test databases
3. **No Mocks**: Avoid mocking repositories or databases
4. **External Dependencies**: Only mock external API calls or services
5. **Test Setup**: Each test should create its own data

## Known Considerations

### ADR-014 Compliance

All services must follow the repository pattern for data access per ADR-014. Direct database queries through SQLAlchemy are prohibited - all data access must happen through repositories.

### ADR-011 Compliance

All services must follow the UTC datetime standards per ADR-011:

1. **Always use datetime_utils.py functions** - Never use raw datetime functions
2. **Store all datetimes in UTC** - Use timezone-aware datetimes in business logic
3. **Use naive datetimes for database operations** - Database stores naive datetimes (semantically UTC)
4. **Use inclusive date ranges** - Use start_of_day and end_of_day for inclusive ranges

### Repository Access through BaseService

All services must:

1. Inherit from BaseService
2. Use _get_repository method for all repository access
3. Pass session and feature flag service to `super().__init__`

```python
class SomeService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
    ):
        super().__init__(session, feature_flag_service)
    
    async def some_method(self):
        # Standard repository access
        repo = await self._get_repository(SomeRepository)
        
        # Polymorphic repository access
        account_repo = await self._get_repository(
            AccountRepository, 
            polymorphic_type="checking"
        )
```

### Service Method Proxying

Services are proxied to enforce feature flags, with method calls intercepted to check if features are enabled before execution. This allows clean separation between business logic and feature enforcement.

### Type-Specific Implementation

Account type-specific functionality is implemented in dedicated modules under `account_types/` to maintain a clean architecture while supporting the full range of account types.

### Specialized Service Pattern

Complex domains like cashflow are implemented as specialized services that each focus on a specific aspect:

1. **Base service**: Shared functionality and repository access
2. **Specialized services**: Each focusing on one domain aspect (e.g., forecasting, historical analysis)
3. **Service composition**: Services can use other services for complex operations
