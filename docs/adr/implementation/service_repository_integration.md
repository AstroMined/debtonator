# Service-Repository Integration Pattern

This document outlines the standard patterns for integrating services with repositories following the implementation of ADR-014 (Repository Layer for CRUD Operations).

## Core Integration Principles

1. **Clear Separation of Concerns**
   - Services own business logic and validation
   - Repositories own data access patterns
   - Each layer has distinct responsibilities

2. **Validation Flow**
   - Services validate data through Pydantic schemas
   - Services perform business logic validation
   - Repositories focus solely on data access

3. **Repository Usage in Services**
   - Services depend on repositories, not database sessions
   - Services orchestrate multiple repository operations
   - Services maintain transaction boundaries

## Service Implementation Pattern

### Constructor Dependency Injection

Services should receive repositories through constructor injection, not database sessions:

```python
class AccountService:
    def __init__(
        self,
        account_repo: AccountRepository,
        statement_repo: StatementHistoryRepository,
        credit_limit_repo: CreditLimitHistoryRepository,
        transaction_repo: TransactionHistoryRepository,
    ):
        self.account_repo = account_repo
        self.statement_repo = statement_repo
        self.credit_limit_repo = credit_limit_repo
        self.transaction_repo = transaction_repo
```

### Service Method Structure

Each service method should follow this structure:

1. **Validation**
   - Validate input data using Pydantic schemas
   - Perform business logic validation
   - Raise appropriate errors for validation failures

2. **Repository Operations**
   - Use repositories for data access operations
   - Orchestrate multiple repository operations when needed
   - Transform repository responses into service-level response objects

3. **Error Handling**
   - Catch and handle repository-specific exceptions
   - Translate data access errors into meaningful business exceptions
   - Maintain clean error boundaries between layers

### Example Service Method

```python
async def update_statement_balance(
    self,
    account_id: int,
    statement_balance: Decimal,
    statement_date: date,
    minimum_payment: Optional[Decimal] = None,
    due_date: Optional[date] = None,
) -> Optional[AccountInDB]:
    """Update an account's statement balance and related information"""
    # Get account using repository
    db_account = await self.account_repo.get(account_id)
    if not db_account:
        return None

    # Validate statement update (business logic)
    is_valid, error_message = await self.validate_statement_update(
        db_account, statement_balance, statement_date, minimum_payment, due_date
    )
    if not is_valid:
        raise ValueError(error_message)

    # Update account using account repository
    account_update = {
        "last_statement_balance": statement_balance,
        "last_statement_date": statement_date
    }
    updated_account = await self.account_repo.update(account_id, account_update)

    # Create statement history using statement repository
    statement_data = StatementHistoryCreate(
        account_id=account_id,
        statement_date=statement_date,
        statement_balance=statement_balance,
        minimum_payment=minimum_payment,
        due_date=due_date
    )
    await self.statement_repo.create(statement_data.model_dump())

    # Return schema-validated response
    return AccountInDB.model_validate(updated_account) if updated_account else None
```

## Dependency Injection Setup

### Repository Dependencies

Repositories should be provided as FastAPI dependencies:

```python
def get_account_repository(db: AsyncSession = Depends(get_db)) -> AccountRepository:
    return AccountRepository(db)

def get_statement_history_repository(
    db: AsyncSession = Depends(get_db)
) -> StatementHistoryRepository:
    return StatementHistoryRepository(db)
```

### Service Dependencies

Services should depend on repositories, not database sessions:

```python
def get_account_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    statement_repo: StatementHistoryRepository = Depends(get_statement_history_repository),
    credit_limit_repo: CreditLimitHistoryRepository = Depends(get_credit_limit_history_repository),
    transaction_repo: TransactionHistoryRepository = Depends(get_transaction_history_repository)
) -> AccountService:
    return AccountService(
        account_repo=account_repo,
        statement_repo=statement_repo,
        credit_limit_repo=credit_limit_repo,
        transaction_repo=transaction_repo
    )
```

### API Endpoint Dependencies

API endpoints should depend on services, not repositories or database sessions:

```python
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

## Transaction Management

### Service-Level Transactions

Services should manage transaction boundaries across multiple repository operations:

```python
async def transfer_funds(
    self, from_account_id: int, to_account_id: int, amount: Decimal
) -> Tuple[AccountInDB, AccountInDB]:
    # Validate business rules
    from_account = await self.account_repo.get(from_account_id)
    if not from_account:
        raise ValueError(f"Source account {from_account_id} not found")
        
    to_account = await self.account_repo.get(to_account_id)
    if not to_account:
        raise ValueError(f"Destination account {to_account_id} not found")
    
    is_valid, error = await self.validate_account_balance(from_account, amount)
    if not is_valid:
        raise ValueError(error)
        
    # Use repository transaction for atomic operations
    async with self.account_repo.transaction() as tx_repo:
        # Deduct from source account
        updated_from = await tx_repo.update_balance(
            from_account_id, amount * Decimal("-1")
        )
        
        # Add to destination account
        updated_to = await tx_repo.update_balance(
            to_account_id, amount
        )
        
        # Create transaction records
        await self.transaction_repo.create({
            "account_id": from_account_id,
            "transaction_type": TransactionType.DEBIT,
            "amount": amount,
            "description": f"Transfer to account {to_account_id}",
            "transaction_date": datetime.now(timezone.utc)
        })
        
        await self.transaction_repo.create({
            "account_id": to_account_id,
            "transaction_type": TransactionType.CREDIT,
            "amount": amount,
            "description": f"Transfer from account {from_account_id}",
            "transaction_date": datetime.now(timezone.utc)
        })
        
    return (
        AccountInDB.model_validate(updated_from),
        AccountInDB.model_validate(updated_to)
    )
```

## Error Handling Pattern

### Repository Error Translation

Repositories should raise specific exceptions that services can handle:

```python
class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass

class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found"""
    pass
    
class DuplicateEntityError(RepositoryError):
    """Raised when attempting to create a duplicate entity"""
    pass
```

### Service Error Handling

Services should catch repository exceptions and translate them to service-level exceptions:

```python
try:
    account = await self.account_repo.get(account_id)
    if not account:
        raise EntityNotFoundError(f"Account with ID {account_id} not found")
        
    # Business logic processing
    
except EntityNotFoundError as e:
    # Pass through entity not found errors
    raise
except DuplicateEntityError as e:
    # Translate to business-specific error
    raise ValueError(f"Account already exists: {str(e)}")
except RepositoryError as e:
    # General repository error handling
    raise ValueError(f"Failed to process account: {str(e)}")
```

## Testing Approach

### Service Testing Pattern

Service tests should use real repositories with database fixtures to validate integration:

```python
@pytest.mark.asyncio
async def test_update_statement_balance(db_session: AsyncSession):
    # Arrange - Create repositories and service
    account_repo = AccountRepository(db_session)
    statement_repo = StatementHistoryRepository(db_session)
    credit_limit_repo = CreditLimitHistoryRepository(db_session)
    transaction_repo = TransactionHistoryRepository(db_session)
    
    service = AccountService(
        account_repo=account_repo,
        statement_repo=statement_repo,
        credit_limit_repo=credit_limit_repo,
        transaction_repo=transaction_repo
    )
    
    # Create test account
    account_data = AccountCreate(
        name="Test Account",
        type="credit",
        available_balance=Decimal("-1000.00"),
        total_limit=Decimal("5000.00")
    )
    account = await account_repo.create(account_data.model_dump())
    
    # Act - Update statement balance
    result = await service.update_statement_balance(
        account_id=account.id,
        statement_balance=Decimal("1500.00"),
        statement_date=date.today(),
        minimum_payment=Decimal("35.00"),
        due_date=date.today() + timedelta(days=21)
    )
    
    # Assert - Verify account updated
    assert result is not None
    assert result.last_statement_balance == Decimal("1500.00")
    assert result.last_statement_date == date.today()
    
    # Verify statement history created
    statements = await statement_repo.get_by_account(account.id)
    assert len(statements) == 1
    assert statements[0].statement_balance == Decimal("1500.00")
    assert statements[0].minimum_payment == Decimal("35.00")
    assert statements[0].due_date == date.today() + timedelta(days=21)
```

### Four-Step Test Pattern

All tests should follow the Arrange-Schema-Act-Assert pattern:

1. **Arrange**: Set up repositories, services, and test data
2. **Schema**: Validate data through Pydantic schemas
3. **Act**: Perform service operations
4. **Assert**: Verify expected outcomes

## Best Practices

1. **Keep Services Focused**
   - Each service should have a clear domain responsibility
   - Services should not know about other services
   - Use factories or dependency injection when coordination is needed

2. **Repository Method Naming**
   - Use consistent naming conventions across all repositories
   - Prefix query methods with `get_` (e.g., `get_by_account`, `get_active_accounts`)
   - Use action verbs for operations (e.g., `create`, `update`, `delete`)

3. **Schema Validation**
   - Always validate data through Pydantic schemas before passing to repositories
   - Use `model_dump()` to convert schemas to dictionaries
   - Include cross-field validation in schema classes when possible

4. **Repository Reuse**
   - Prefer composition over inheritance for repository functionality
   - Use higher-level repositories to orchestrate operations across multiple base repositories
   - Create specialized query methods in repositories, not in services

## Conclusion

The service-repository integration pattern provides:

1. Clear separation of business logic and data access concerns
2. Improved testability through dependency injection
3. Better maintainability with standardized error handling
4. Consistent transaction management across operations
5. Simplified service implementations focused on business logic

Following these patterns will ensure a consistent approach across the application and make future extensions more straightforward.
