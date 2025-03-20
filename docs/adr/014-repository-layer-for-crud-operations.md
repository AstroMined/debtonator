# ADR-014: Repository Layer for CRUD Operations

## Status
Accepted - In Implementation

## Context
Our services layer currently handles both CRUD operations and business logic, leading to several architectural challenges:

1. **Violation of Single Responsibility Principle (SRP)**: Services are responsible for both data access and business logic
2. **Code duplication (DRY violations)**: Common CRUD patterns are repeated across service classes
3. **Excessive complexity**: Services grow large and complex, mixing multiple concerns
4. **Testing challenges**: Services with mixed responsibilities are harder to test effectively
5. **Reduced maintainability**: Changes to data access patterns require updates across multiple service files

The current implementation creates a "spaghetti code" situation where business logic is intertwined with data access, making it difficult to evolve either aspect independently.

## Decision
We will introduce a repository layer dedicated to CRUD operations for all SQLAlchemy models. This layer will:

1. Provide a consistent interface for database operations
2. Encapsulate SQLAlchemy-specific implementation details
3. Handle common data access patterns in a single location
4. Support transaction management across operations

Services will use these repositories for data access while focusing on business logic, validation, and orchestration.

## Detailed Design

### 1. Base Repository
We'll create a generic base repository with type parameters for the model and primary key:

```python
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)
PKType = TypeVar("PKType")

class BaseRepository(Generic[ModelType, PKType]):
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model_class = model_class

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model_class(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: PKType) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalars().first()

    async def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        query = select(self.model_class).offset(skip).limit(limit)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.where(getattr(self.model_class, field) == value)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(
        self, 
        id: PKType, 
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if not db_obj:
            return None
            
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
            
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: PKType) -> bool:
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        return result.rowcount > 0
```

### 2. Model-Specific Repositories

For each model, we'll create a specific repository that inherits from BaseRepository and adds model-specific methods:

```python
from src.models.accounts import Account
from src.database.base import Base
from src.database.database import AsyncSession

class AccountRepository(BaseRepository[Account, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Account)
        
    # Additional model-specific methods
    async def get_by_name(self, name: str) -> Optional[Account]:
        result = await self.session.execute(
            select(Account).where(Account.name == name)
        )
        return result.scalars().first()
```

### 3. Repository Factory

To simplify dependency injection, we'll create a repository factory:

```python
from typing import Type, TypeVar, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository

T = TypeVar('T', bound=BaseRepository)

class RepositoryFactory:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repositories: Dict[Type[BaseRepository], BaseRepository] = {}
    
    def get_repository(self, repository_class: Type[T]) -> T:
        if repository_class not in self._repositories:
            self._repositories[repository_class] = repository_class(self.session)
        return self._repositories[repository_class]
```

### 4. Service Integration

Services will use repositories for data access:

```python
class AccountService:
    def __init__(self, account_repo: AccountRepository, statement_repo: StatementHistoryRepository):
        self.account_repo = account_repo
        self.statement_repo = statement_repo
    
    async def update_statement_balance(
        self,
        account_id: int,
        statement_balance: Decimal,
        statement_date: date,
        minimum_payment: Optional[Decimal] = None,
        due_date: Optional[date] = None
    ) -> Optional[AccountInDB]:
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        # Validate statement update
        is_valid, error_message = await self.validate_statement_update(
            db_account,
            statement_balance,
            statement_date,
            minimum_payment,
            due_date
        )
        if not is_valid:
            raise ValueError(error_message)

        # Update current statement info
        await self.account_repo.update(
            account_id,
            {
                "last_statement_balance": statement_balance,
                "last_statement_date": statement_date
            }
        )
        
        # Create statement history entry
        await self.statement_repo.create(
            {
                "account_id": account_id,
                "statement_date": statement_date,
                "statement_balance": statement_balance,
                "minimum_payment": minimum_payment,
                "due_date": due_date
            }
        )
        
        return await self.get_account(account_id)
```

### 5. Dependency Injection

FastAPI dependency injection will provide repositories to services:

```python
def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return AccountRepository(db)

def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    statement_repo: StatementHistoryRepository = Depends(get_statement_history_repository)
) -> AccountService:
    return AccountService(account_repo, statement_repo)

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service)
):
    account = await account_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
```

### 6. Repository Features

#### 6.1 Advanced Querying
Repositories will support advanced querying with joins, ordering, and filtering:

```python
async def get_accounts_with_statements(
    self, 
    after_date: Optional[date] = None
) -> List[Account]:
    query = (
        select(Account)
        .outerjoin(StatementHistory)
        .options(joinedload(Account.statements))
    )
    
    if after_date:
        query = query.where(StatementHistory.statement_date >= after_date)
    
    result = await self.session.execute(query)
    return result.unique().scalars().all()
```

#### 6.2 Pagination
Standardized pagination across repositories:

```python
async def get_paginated(
    self,
    page: int = 1,
    items_per_page: int = 20,
    **filters
) -> Tuple[List[ModelType], int]:
    # Calculate offset
    skip = (page - 1) * items_per_page
    
    # Count total items
    count_query = select(func.count()).select_from(self.model_class)
    for field, value in filters.items():
        if hasattr(self.model_class, field):
            count_query = count_query.where(getattr(self.model_class, field) == value)
    
    result = await self.session.execute(count_query)
    total = result.scalar_one()
    
    # Get items for current page
    items = await self.get_multi(skip=skip, limit=items_per_page, filters=filters)
    
    return items, total
```

#### 6.3 Transaction Support
Repositories will work with session-level transactions:

```python
async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
    db_objects = []
    for obj in objects:
        db_obj = self.model_class(**obj)
        self.session.add(db_obj)
        db_objects.append(db_obj)
    
    await self.session.flush()
    
    # Refresh all objects
    for obj in db_objects:
        await self.session.refresh(obj)
    
    return db_objects
```

## Implementation Approach
The implementation will follow these phases:

1. **Phase 1: Foundation**
   - Implement BaseRepository
   - Create repository factory
   - Add dependency injection system

2. **Phase 2: Core Repositories**
   - Implement repositories for key models
   - Create initial integration tests

3. **Phase 3: Service Refactoring**
   - Refactor AccountService as proof-of-concept
   - Validate approach with comprehensive tests

4. **Phase 4: Full Implementation**
   - Implement remaining repositories
   - Refactor all services to use repositories
   - Migrate tests to use new architecture

5. **Phase 5: Optimization**
   - Add specialized repository methods
   - Improve performance of common queries
   - Add advanced features (bulk operations, custom filters)

## Testing Strategy
We will primarily use integration tests with real DB fixtures to validate repository behavior:

1. **Test fixture setup**: Create test database with predefined data
2. **CRUD operation tests**: Verify basic operations work correctly
3. **Transaction tests**: Ensure operations respect transaction boundaries
4. **Complex query tests**: Validate joins, filters, and pagination
5. **Edge case tests**: Test error cases and boundary conditions

## Consequences

### Positive
- **Improved SRP compliance**: Clear separation between data access and business logic
- **Reduced duplication**: Common CRUD patterns implemented in one place
- **Better testability**: Easier to test services and repositories independently
- **More maintainable code**: Smaller, more focused components
- **Standardized data access**: Consistent patterns across the application
- **Easier to extend**: New models just need repository implementation
- **Better transaction support**: Clearer transaction boundaries
- **Performance optimization potential**: Ability to optimize common queries in one place

### Negative
- **Additional abstraction**: Adds another layer to the architecture
- **Migration effort**: Requires significant refactoring of existing code
- **Learning curve**: New pattern to understand for future developers
- **Potential for over-abstraction**: Need to maintain pragmatic approach

### Neutral
- **Changed dependency flow**: Services depend on repositories instead of directly on session
- **Different testing approach**: Focus shifts to integration testing for repositories

## Alternatives Considered

### Direct ORM Use in Services
Continuing to use SQLAlchemy directly in services is simpler but doesn't address the current issues with code duplication and mixed responsibilities.

### Domain Driven Design Repositories
A more complex repository pattern based on DDD principles was considered but deemed too complex for our needs. Our approach is simpler while still providing the key benefits.

### Query Object Pattern
Using query objects to encapsulate database queries was considered as an alternative. While powerful, it adds more complexity than needed for our use case.