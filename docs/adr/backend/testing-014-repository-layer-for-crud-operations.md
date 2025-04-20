# Testing Strategy: Repository Layer (ADR-014)

## Overview

This document outlines the testing approach for the repository layer implementation described in ADR-014. The repository layer requires a specific testing methodology that differs from typical unit tests, focusing on integration testing with real database fixtures.

## Core Testing Principles

1. **Real Objects Testing Philosophy**
   - No mocks policy: unittest.mock and MagicMock are strictly prohibited
   - Use real database fixtures that reset between tests
   - Test with real Pydantic schemas, not test dummies
   - Test cross-layer validation with actual repository objects

2. **Validation Flow Simulation**
   - Tests must simulate the service-to-repository validation flow
   - All test data must pass through Pydantic schemas before reaching repositories
   - Repositories should never receive raw, unvalidated dictionaries in tests
   - This approach validates both repository functionality and proper validation patterns

## The Arrange-Schema-Act-Assert Pattern

All repository tests must follow the Arrange-Schema-Act-Assert pattern to properly simulate the validation flow:

1. **Arrange**: Set up any test fixtures and dependencies needed for the test.
2. **Schema**: Create and validate data through appropriate Pydantic schemas.
3. **Act**: Convert validated schemas to dictionaries and pass to repository methods.
4. **Assert**: Verify that the repository operation produced the expected results.

```python
@pytest.mark.asyncio
async def test_repository_operation(repo_fixture, other_fixtures):
    """Test description that explains the purpose of the test."""
    # 1. ARRANGE: Setup any test dependencies
    # ... setup code
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    entity_schema = create_entity_schema(
        key1="value1",
        key2="value2"
    )
    
    # Convert validated schema to dict for repository
    validated_data = entity_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    result = await repository.method(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.key1 == "value1"
    assert result.key2 == "value2"
```

## Schema Factory Implementation

Instead of creating separate implementations for each repository test, use schema factories to create valid schema instances:

1. **Consult the Schema Factories Directory**: See `tests/helpers/schema_factories/` for existing factories.

2. **Add New Factory Functions When Needed**: When testing a repository that needs a new schema factory:
   - Create or update the appropriate domain file in `schema_factories/`
   - Add the factory function following the established pattern
   - Export the function in `__init__.py`

3. **Use Factories in Tests**: Import and use factory functions in your tests:
   ```python
   from tests.helpers.schema_factories import create_entity_schema
   
   entity_schema = create_entity_schema(name="Test", value=100)
   ```

4. **Follow Factory Function Guidelines**:
   - Provide reasonable defaults for all non-required fields
   - Use type hints for parameters and return values
   - Document parameters, defaults, and return types
   - Allow overriding any field with `**kwargs`
   - Return validated schema instances, not dictionaries

Schema factories provide several benefits:
- Consistent test data across multiple tests
- Proper field defaults for optional fields
- Encapsulation of complex data structures
- Better test maintainability when schemas change

## Testing Database Setup

Repository tests require a real database with proper test isolation:

```python
@pytest.fixture
async def db_session():
    """Create a clean test database session for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        future=True,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = AsyncSession(
        engine, expire_on_commit=False
    )
    
    try:
        yield async_session
    finally:
        await async_session.close()
        await engine.dispose()
```

## Repository Test Organization

Repository tests should be organized into logical categories:

1. **CRUD Tests**
   - Basic create, read, update, delete operations
   - Validation of simple relationships
   - Error handling for standard operations

2. **Advanced Tests**
   - Complex query operations
   - Relationship loading tests
   - Pagination and filtering
   - Transaction boundary tests

Example directory structure:
```
tests/integration/repositories/
  ├── crud/
  │   ├── test_account_repository.py
  │   ├── test_bill_repository.py
  │   └── ...
  └── advanced/
      ├── test_account_repository_advanced.py
      ├── test_bill_repository_advanced.py
      └── ...
```

## Testing Polymorphic Repositories

Polymorphic repositories require special testing considerations:

1. **Type-Specific Entity Creation**
   - Always use `create_typed_entity()` instead of base `create()` method
   - Test with specific concrete subclasses
   - Verify polymorphic identity is maintained

2. **Field Validation Testing**
   - Test that type-specific fields are properly filtered
   - Verify required fields are enforced
   - Test that invalid fields raise appropriate errors

3. **Type Registry Integration**
   - Test integration with type registries
   - Verify lookup of proper model classes
   - Test error handling for invalid types

```python
# Example polymorphic repository test
@pytest.mark.asyncio
async def test_create_typed_account(db_session):
    """Test creating a typed account through the polymorphic repository."""
    # Arrange
    repo = AccountRepository(db_session)
    
    # Schema - use schema factory for checking account
    account_schema = create_checking_account_schema(
        name="My Checking",
        available_balance=Decimal("1000.00"),
        overdraft_limit=Decimal("100.00")
    )
    
    # Act - use create_typed_entity rather than create
    account = await repo.create_typed_entity(
        "checking", account_schema.model_dump()
    )
    
    # Assert
    assert account is not None
    assert account.name == "My Checking"
    assert account.account_type == "checking"
    assert account.available_balance == Decimal("1000.00")
    assert account.overdraft_limit == Decimal("100.00")
```

## Testing Transaction Boundaries

Repository tests should verify transaction behavior:

1. **Rollback Testing**
   - Test transaction rollback on errors
   - Verify changes are not persisted after exceptions
   - Test proper cleanup after failed operations

2. **Atomic Operation Testing**
   - Verify that multi-operation transactions are atomic
   - Test that related entities are created together
   - Verify partial failures don't leave inconsistent data

```python
@pytest.mark.asyncio
async def test_transaction_rollback(db_session):
    """Test that transactions roll back on errors."""
    # Arrange
    repo = AccountRepository(db_session)
    account_schema = create_account_schema(name="Test Account")
    
    # Create initial account
    account = await repo.create(account_schema.model_dump())
    account_id = account.id
    
    # Act - attempt invalid update that should fail and roll back
    try:
        async with repo.transaction() as tx_repo:
            # This update should succeed
            await tx_repo.update(account_id, {"name": "Updated Name"})
            
            # This update should fail and cause rollback
            await tx_repo.update(999999, {"name": "Nonexistent"})
    except Exception:
        pass  # Expected exception
        
    # Assert - verify the first update was rolled back
    updated_account = await repo.get(account_id)
    assert updated_account.name == "Test Account"  # Original name, not "Updated Name"
```

## Testing Error Handling

Repository tests should verify proper error handling:

1. **Common Error Scenarios**
   - Test that entity not found errors are handled appropriately
   - Verify duplicate entity errors are detected and raised
   - Test validation failures at the repository level
   - Verify constraint violation handling

2. **Custom Error Types**
   - Test that repository-specific error types are raised
   - Verify error messages contain appropriate context
   - Test error hierarchy for exception handling
   - Verify error translation between layers

```python
@pytest.mark.asyncio
async def test_entity_not_found_error(db_session):
    """Test that appropriate error is raised when entity is not found."""
    repo = AccountRepository(db_session)
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError) as excinfo:
        await repo.get_with_validation(999999)
        
    # Verify error message
    assert "Account with ID 999999 not found" in str(excinfo.value)
```

## Testing Datetime Handling

Repository tests should verify proper datetime handling with UTC:

1. **Timezone Awareness**
   - Test that datetimes are stored and retrieved correctly
   - Verify that timezone information is handled properly
   - Test date range filters with timezone considerations
   - Verify comparison operations with timezone-aware datetimes

2. **Naive vs. Aware Datetimes**
   - Test handling of naive datetimes in database operations
   - Verify conversion between naive and aware datetimes
   - Test utility functions for datetime standardization
   - Verify consistent behavior across database operations

```python
@pytest.mark.asyncio
async def test_datetime_handling(db_session):
    """Test handling of timezone-aware datetimes."""
    # Arrange
    repo = StatementHistoryRepository(db_session)
    now = datetime.now(UTC)
    account_id = 1
    
    # Create schema with timezone-aware datetime
    statement_schema = create_statement_history_schema(
        account_id=account_id,
        statement_date=now,
        due_date=now + timedelta(days=25)
    )
    
    # Act
    statement = await repo.create(statement_schema.model_dump())
    
    # Assert - retrieve and verify datetime values
    retrieved = await repo.get(statement.id)
    assert datetime_equals(retrieved.statement_date, now)
    assert datetime_equals(retrieved.due_date, now + timedelta(days=25))
    
    # Test date range filter
    start_date = now - timedelta(days=1)
    end_date = now + timedelta(days=1)
    
    results = await repo.get_by_date_range(start_date, end_date)
    assert len(results) == 1
    assert results[0].id == statement.id
```

## Testing Bill Splits with Polymorphic Account Types

Bill split repositories require special testing due to their complex validation logic:

1. **Split Validation Testing**
   - Test that split amounts sum to the total bill amount
   - Verify account validation in split operations
   - Test automatic primary account split creation
   - Verify split amount recalculation when total changes

2. **Transaction Boundary Testing**
   - Test that all splits are created/updated in a single transaction
   - Verify rollback on validation failures
   - Test update scenarios with changed split distribution
   - Verify partial update handling with missing splits

```python
@pytest.mark.asyncio
async def test_bill_splits_with_polymorphic_accounts(db_session):
    """Test creating bill splits with different account types."""
    # Arrange - Create different account types
    account_repo = AccountRepository(db_session)
    bill_repo = LiabilityRepository(db_session)
    bill_split_repo = BillSplitRepository(db_session)
    
    # Create a checking account
    checking_schema = create_checking_account_schema(name="Checking")
    checking = await account_repo.create_typed_entity("checking", checking_schema.model_dump())
    
    # Create a credit account
    credit_schema = create_credit_account_schema(name="Credit")
    credit = await account_repo.create_typed_entity("credit", credit_schema.model_dump())
    
    # Create a bill with primary account
    bill_schema = create_bill_schema(
        name="Split Bill",
        amount=Decimal("100.00"),
        primary_account_id=checking.id
    )
    bill = await bill_repo.create(bill_schema.model_dump())
    
    # Act - Create split between accounts
    splits = [
        create_bill_split_schema(
            liability_id=bill.id,
            account_id=checking.id,
            amount=Decimal("60.00")
        ).model_dump(),
        create_bill_split_schema(
            liability_id=bill.id,
            account_id=credit.id,
            amount=Decimal("40.00")
        ).model_dump()
    ]
    
    result = await bill_split_repo.bulk_create_splits(bill.id, splits)
    
    # Assert
    assert len(result) == 2
    
    # Verify split amounts
    checking_split = next(s for s in result if s.account_id == checking.id)
    credit_split = next(s for s in result if s.account_id == credit.id)
    
    assert checking_split.amount == Decimal("60.00")
    assert credit_split.amount == Decimal("40.00")
    
    # Verify total
    total = sum(s.amount for s in result)
    assert total == Decimal("100.00")
```

## Test Repository With Relationships

Tests should verify relationship handling:

1. **Eager Loading Testing**
   - Test eager loading with joinedload
   - Verify selectinload for collections
   - Test multiple-level relationship loading
   - Verify performance with relationship loading options

2. **Relationship Filter Testing**
   - Test filtering based on relationship attributes
   - Verify joins for relationship filtering
   - Test complex relationship constraints
   - Verify performance for relationship-based filters

```python
@pytest.mark.asyncio
async def test_repository_with_relationships(db_session):
    """Test retrieving entities with their relationships."""
    # Arrange - Create parent-child relationship
    parent_repo = CategoryRepository(db_session)
    bill_repo = LiabilityRepository(db_session)
    
    parent_schema = create_category_schema(name="Parent")
    parent = await parent_repo.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Child",
        parent_id=parent.id
    )
    child = await parent_repo.create(child_schema.model_dump())
    
    # Create bills in child category
    bill1_schema = create_bill_schema(
        name="Bill 1",
        category_id=child.id,
        amount=Decimal("50.00")
    )
    bill2_schema = create_bill_schema(
        name="Bill 2",
        category_id=child.id,
        amount=Decimal("75.00")
    )
    
    await bill_repo.create(bill1_schema.model_dump())
    await bill_repo.create(bill2_schema.model_dump())
    
    # Act - Get parent with children and bills
    result = await parent_repo.get_with_children_and_bills(parent.id)
    
    # Assert
    assert result.id == parent.id
    assert len(result.children) == 1
    assert result.children[0].id == child.id
    assert len(result.children[0].bills) == 2
    assert sum(b.amount for b in result.children[0].bills) == Decimal("125.00")
```

## Comprehensive Testing Patterns

The repository testing strategy should include these additional patterns:

1. **Proper Test Organization**
   - Group related tests together
   - Use descriptive test names
   - Properly document test purpose and assertions
   - Organize test fixtures for clarity

2. **Complete Test Coverage**
   - Test all repository methods
   - Cover both success and error paths
   - Test edge cases and boundary conditions
   - Verify performance for large datasets

3. **Consistent Test Patterns**
   - Follow the Arrange-Schema-Act-Assert pattern in all tests
   - Use schema factories consistently
   - Maintain consistent assertion styles
   - Document test patterns for new developers

4. **Test Environment Management**
   - Ensure tests run in isolation
   - Reset database state between tests
   - Handle connection lifecycle properly
   - Minimize test runtime while maintaining coverage

## Reference Implementation

For a complete reference implementation of the repository test pattern, see:
`tests/integration/repositories/test_balance_reconciliation_repository.py`

This file demonstrates:
- Proper arrange-schema-act-assert pattern
- Complete schema validation flow
- Comprehensive test coverage
- Clear organization of related tests
- Proper handling of transactions and errors

## Conclusion

Following these testing patterns ensures that the repository layer is thoroughly tested with a focus on real-world usage patterns. The integration-first approach with real database fixtures provides confidence in the repository implementation while avoiding the pitfalls of mock-based testing.

The Arrange-Schema-Act-Assert pattern ensures that tests validate both the repository functionality and the proper validation flow, making the tests more realistic and effective at catching issues before they reach production.
