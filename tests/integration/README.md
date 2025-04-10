# Integration Tests

This directory contains integration tests for components of the Debtonator application that cross layer boundaries. Integration tests verify that different components work together correctly and follow the "Real Objects Testing Philosophy" established in ADR-014.

## What is an Integration Test?

Integration tests in Debtonator verify the functionality of components that span multiple layers of the application. They ensure that components interact correctly while maintaining proper transaction boundaries and error handling.

The following components require integration tests:
- **Repositories** (`repositories/`): Data access components that interact with the database
- **Services** (`services/`): Business logic components that use repositories
- **API** (`api/`): API endpoints that use services

## Directory Structure

Each subdirectory follows the structure of the corresponding source code directory:

```
integration/
├── repositories/    # Tests for repository layer
├── services/        # Tests for service layer
└── api/             # Tests for API endpoints
```

## Testing Principles

1. **Cross-Layer Testing**: Test interactions between multiple layers
2. **Real Objects**: Use real objects rather than mocks (per ADR-014)
3. **Real Database**: Use a real test database that resets between tests
4. **Proper Isolation**: Each test should be independent of others
5. **Clear Test Flow**: Use Arrange-Act-Assert or similar pattern

## Services Layer Tests

Services span multiple layers by design:
- They use repositories to access data
- They implement business logic that affects multiple entities
- They handle validation and error translation

Example service test:
```python
async def test_create_payment(payment_service, db_session):
    """Test creating a payment with service layer."""
    # Arrange - create test data
    account = await create_test_checking_account(db_session)
    bill = await create_test_bill(db_session, primary_account_id=account.id)
    
    # Act - use service to create payment
    payment = await payment_service.create_payment(
        bill_id=bill.id,
        account_id=account.id,
        amount=Decimal("100.00"),
        payment_date=naive_utc_now()
    )
    
    # Assert - verify results
    assert payment.id is not None
    assert payment.amount == Decimal("100.00")
    assert payment.bill_id == bill.id
    assert payment.account_id == account.id
    
    # Verify bill state updated
    updated_bill = await payment_service.bill_repository.get_by_id(bill.id)
    assert updated_bill.is_paid is True
```

## Repository Layer Tests

Repository tests verify data access patterns and database interactions:
- CRUD operations
- Complex queries
- Transaction handling

Example repository test:
```python
async def test_find_accounts_by_type(account_repository, db_session):
    """Test finding accounts by type."""
    # Arrange - create test accounts
    checking = await create_test_checking_account(db_session)
    savings = await create_test_savings_account(db_session)
    
    # Act - find accounts by type
    checking_accounts = await account_repository.find_by_type("checking")
    
    # Assert - verify correct accounts returned
    assert len(checking_accounts) == 1
    assert checking_accounts[0].id == checking.id
    assert checking_accounts[0].account_type == "checking"
```

## API Layer Tests

API tests verify that API endpoints work correctly:
- Request validation
- Response formatting
- Error handling

Example API test:
```python
async def test_get_account_endpoint(client, db_session):
    """Test GET /accounts/{account_id} endpoint."""
    # Arrange - create test account
    account = await create_test_checking_account(db_session)
    
    # Act - make request to endpoint
    response = await client.get(f"/accounts/{account.id}")
    
    # Assert - verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == account.id
    assert data["name"] == account.name
    assert data["account_type"] == "checking"
```

## Learn More

For detailed guidance on testing specific components, see the README.md in each subdirectory:

- [Repository Tests](./repositories/README.md)
- [Service Tests](./services/README.md)
- [API Tests](./api/README.md)
