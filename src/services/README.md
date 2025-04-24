# Services Layer

## Purpose

The services layer is the heart of Debtonator's business logic, orchestrating operations between the API layer and repositories. Services encapsulate domain-specific operations, enforce business rules, and coordinate multi-entity workflows.

## Related Documentation

- [Repository Layer README](/code/debtonator/src/repositories/README.md)
- [ADR-014: Repository Layer for CRUD Operations](/code/debtonator/docs/adr/backend/014-repository-layer-for-crud-operations.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md)

## Architecture

The services layer:

1. **Consumes repositories**: All data access must occur through repositories
2. **Enforces business rules**: Validation logic not appropriate for schemas or models
3. **Orchestrates workflows**: Manages multi-step business processes
4. **Handles transactions**: Ensures data integrity across multiple operations
5. **Implements feature flags**: Services are wrapped by feature flag proxies

```
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
│   ├── base.py
│   ├── forecast_service.py
│   ├── main.py
│   └── ...
├── interceptors/             # Service method interceptors
│   └── feature_flag_interceptor.py
└── proxies/                  # Service method proxies
    └── feature_flag_proxy.py
```

## Implementation Patterns

### Repository Usage Pattern

Services must use repositories for all data access:

```python
# ✓ CORRECT: Using repository for data access
async def get_account(self, account_id: int) -> Optional[Account]:
    return await self.account_repository.get(account_id)

# ✗ INCORRECT: Direct database access
async def get_account(self, account_id: int) -> Optional[Account]:
    query = select(Account).where(Account.id == account_id)
    result = await self.session.execute(query)
    return result.scalar_one_or_none()
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

### Service Factory Pattern

Services are instantiated through the ServiceFactory for dependency injection:

```python
# Factory creates service with appropriate repositories
account_service = service_factory.create_account_service()

# Service methods use injected repositories
account = await account_service.get_account(account_id)
```

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

All services must follow the repository pattern for data access per ADR-014. Direct database queries through SQLAlchemy should be migrated to repository calls.

### Service Method Proxying

Services are proxied to enforce feature flags, with method calls intercepted to check if features are enabled before execution. This allows clean separation between business logic and feature enforcement.

### Type-Specific Implementation

Account type-specific functionality is implemented in dedicated modules under `account_types/` to maintain a clean architecture while supporting the full range of account types.
