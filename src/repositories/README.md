# Repository Layer

## Purpose

The repository layer provides a clean abstraction over database access, following the Repository Pattern. It encapsulates all data access operations, enabling services to work with domain objects without directly interacting with the database.

## Related Documentation

- [Service Layer README](/code/debtonator/src/services/README.md)
- [ADR-014: Repository Layer for CRUD Operations](/code/debtonator/docs/adr/backend/014-repository-layer-for-crud-operations.md)
- [Account Types Repository README](/code/debtonator/src/repositories/account_types/README.md)

## Architecture

The repository layer sits between the service layer and the database:

```
Service Layer → Repository Layer → Database Layer
```

Key components include:

```
src/repositories/
├── base.py                   # BaseRepository with generic CRUD operations
├── polymorphic_base.py       # PolymorphicBaseRepository for type-specific entities
├── factory.py                # RepositoryFactory for instantiation
├── accounts.py               # AccountRepository implementation
├── liabilities.py            # LiabilityRepository implementation
├── payments.py               # PaymentRepository implementation
├── account_types/            # Type-specific repository modules 
│   ├── banking/
│   │   ├── checking.py
│   │   ├── credit.py
│   │   └── ...
├── proxies/                  # Repository proxies
│   └── feature_flag_proxy.py
└── ...                       # Other model-specific repositories
```

## Implementation Patterns

### Base Repository Pattern

The `BaseRepository` provides common CRUD operations for all entity types:

```python
class BaseRepository(Generic[ModelType, PKType]):
    """Base repository for CRUD operations."""
    
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model_class = model_class
    
    async def get(self, id: PKType) -> Optional[ModelType]:
        """Get entity by primary key."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalars().first()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new entity."""
        db_obj = self.model_class(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    # Additional CRUD methods...
```

### Polymorphic Repository Pattern

The `PolymorphicBaseRepository` handles type-specific entities:

```python
class PolymorphicBaseRepository(BaseRepository[PolyModelType, PKType]):
    """Base repository for polymorphic entities."""
    
    discriminator_field: ClassVar[str] = "type"
    registry = None
    
    async def create(self, obj_in: Dict[str, Any]) -> PolyModelType:
        """Disabled for polymorphic repositories."""
        raise NotImplementedError(
            "Direct creation is disabled. Use create_typed_entity() instead."
        )
    
    async def create_typed_entity(
        self, 
        entity_type: str, 
        data: Dict[str, Any]
    ) -> PolyModelType:
        """Create a new entity with the specified polymorphic type."""
        # Implementation...
```

### Repository Module Pattern

Type-specific repository functionality is implemented as modules that are dynamically loaded:

```python
# RepositoryFactory dynamically loads type-specific functions
account_repo = await RepositoryFactory.create_account_repository(
    session=session,
    account_type="checking"
)

# Type-specific function from checking.py is available
overdraft_accounts = await account_repo.get_accounts_with_overdraft_protection()
```

### Repository Factory Pattern

The `RepositoryFactory` creates and manages repository instances:

```python
class RepositoryFactory:
    """Factory for creating repositories."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repositories = {}
    
    def get_repository(self, repository_class: Type[T]) -> T:
        """Get or create a repository instance."""
        if repository_class not in self._repositories:
            self._repositories[repository_class] = repository_class(self.session)
        return self._repositories[repository_class]
    
    @classmethod
    async def create_account_repository(
        cls,
        session: AsyncSession,
        account_type: Optional[str] = None
    ) -> AccountRepository:
        """Create an account repository with specialized functionality."""
        # Implementation...
```

### Feature Flag Proxy Pattern

Repository operations can be wrapped with feature flag proxies:

```python
# Create a repository with feature flag enforcement
account_repo = RepositoryFactory.create_account_repository(session)
proxied_repo = FeatureFlagRepositoryProxy(
    account_repo, 
    feature_flag_service,
    config_provider
)

# Operations will be checked against feature flags
account = await proxied_repo.get(account_id)  # Checked against feature flags
```

## Key Responsibilities

1. **Data Access**: All database operations must go through repositories
2. **Entity Mapping**: Converting between database models and domain objects
3. **Query Construction**: Building and executing database queries
4. **Transaction Handling**: Managing database transactions
5. **Polymorphic Handling**: Type-specific entity operations

## Testing Strategy

1. **Integration Testing**: Repositories are tested with a real test database
2. **No Mocks**: Avoid mocking the database or repository dependencies
3. **Test Database**: Each test creates a fresh database state
4. **Comprehensive Coverage**: Test all repository methods
5. **Edge Cases**: Test with NULL values, empty results, and error conditions

## Known Considerations

### Direct Database Access Prohibition

As mandated by ADR-014, services should never access the database directly. All data operations must go through repositories, which provides:

- Clear separation of concerns
- Consistent data access patterns
- Simplified testing
- Centralized transaction management
- Ability to change database implementation

### SQLAlchemy 2.0 Compatibility

Repositories use SQLAlchemy 2.0 async patterns:

```python
# ✓ CORRECT: Using select() function with execute()
stmt = select(Model).where(Model.id == some_id)
result = await db_session.execute(stmt)
item = result.scalars().first()

# ✗ INCORRECT: Using legacy query() method
items = (await db_session.execute(db_session.query(Model))).scalars().all()
```

### Specialized Repository Methods

When implementing specialized repository methods:

1. Focus on a single responsibility
2. Keep complex queries in the repository, not in services
3. Return domain objects, not ORM constructs
4. Use descriptive method names that reflect the business domain
5. Document complex queries with comments

### Datetime Handling

Repositories must follow these datetime handling conventions:

1. Store all datetime values in UTC timezone
2. Use timezone-aware objects for business logic
3. Strip timezone info before storing in the database
4. Re-add timezone info when retrieving from the database
