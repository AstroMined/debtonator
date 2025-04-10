# Unit Tests for Service Layer

This directory contains unit tests for the service components in the Debtonator application. These tests validate the business logic, repository integration, and cross-entity operations of the service layer while adhering to the "Real Objects Testing Philosophy" from ADR-014.

## Directory Structure

The service tests directory structure mirrors the structure of the `src/services` directory:

```
unit/services/
├── __init__.py
├── test_account_service.py
├── test_bill_service.py
├── test_payment_service.py
├── test_income_service.py
├── test_cashflow_service.py
├── test_feature_flag_service.py
├── ...
└── account_types/
    ├── __init__.py
    ├── banking/
    │   ├── __init__.py
    │   ├── test_checking_service.py
    │   ├── test_savings_service.py
    │   ├── test_credit_service.py
    │   ├── test_bnpl_service.py
    │   └── ...
    ├── bill/
    ├── investment/
    └── loan/
```

## Naming Convention

All test files follow a consistent naming convention:

- Files must start with the prefix `test_`
- The remainder should match the name of the file in `src/services` being tested
- Example: `src/services/account_service.py` → `test_account_service.py`

## Service Layer Testing Principles

The service layer is where Debtonator's core business logic resides. When testing services, follow these key principles:

1. **Use Real Repositories**: Following ADR-014, always use real repositories instead of mocks
2. **Use Real Database**: Run tests against a real SQLite database, not mock data
3. **Test Business Logic**: Focus on testing business rules and service-specific logic
4. **Test Cross-Entity Operations**: Verify operations that span multiple entities
5. **Test Layer Integration**: Verify correct interaction between services and repositories
6. **Test Error Handling**: Verify services properly handle and translate errors
7. **Test Feature Flag Integration**: Verify feature flags control behavior appropriately
8. **Follow UTC Datetime Compliance**: Adhere to ADR-011 for datetime handling

## Setting Up Service Tests

Services depend on repositories and other components. Set them up properly:

```python
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account_service import AccountService
from src.repositories.account_repository import AccountRepository
from src.errors.account_errors import AccountNotFoundError
from tests.fixtures.models.fixture_accounts_models import create_test_checking_account

@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession):
    """Create an account repository for testing."""
    return AccountRepository(db_session)

@pytest_asyncio.fixture
async def account_service(account_repository):
    """Create an account service with repository dependency."""
    return AccountService(account_repository)

async def test_account_service_get_by_id(account_service, db_session):
    """Test retrieving account by ID."""
    # Create test account
    account = await create_test_checking_account(db_session)
    
    # Test service method
    retrieved = await account_service.get_account_by_id(account.id)
    
    assert retrieved is not None
    assert retrieved.id == account.id
    assert retrieved.name == account.name
```

## Service Testing Focus Areas

### 1. Business Logic

Test that business logic is correctly implemented:

```python
async def test_account_service_calculate_total_balance(account_service, db_session):
    """Test total balance calculation business logic."""
    # Create test accounts
    checking = await create_test_checking_account(
        db_session, 
        name="Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    savings = await create_test_savings_account(
        db_session, 
        name="Savings",
        available_balance=Decimal("2000.00"),
        current_balance=Decimal("2000.00")
    )
    credit = await create_test_credit_account(
        db_session, 
        name="Credit Card",
        credit_limit=Decimal("3000.00"), 
        current_balance=Decimal("500.00")
    )
    
    # Test business logic
    total_balance = await account_service.calculate_total_balance()
    
    # Debit accounts add, credit accounts subtract
    expected_balance = Decimal("1000.00") + Decimal("2000.00") - Decimal("500.00")
    assert total_balance == expected_balance
```

### 2. Complex Bill Split Functionality

Bill splitting is a core feature of Debtonator that needs thorough testing:

```python
async def test_bill_service_split_creation(bill_service, db_session):
    """Test bill split creation and validation."""
    # Create test accounts
    checking = await create_test_checking_account(db_session)
    savings = await create_test_savings_account(db_session)
    credit = await create_test_credit_account(db_session)
    
    # Create test bill with primary account
    bill = await create_test_bill(
        db_session,
        name="Split Test Bill",
        amount=Decimal("1200.00"),
        primary_account_id=checking.id
    )
    
    # Create splits via service
    splits = [
        {"account_id": savings.id, "amount": Decimal("400.00")},
        {"account_id": credit.id, "amount": Decimal("300.00")}
    ]
    
    await bill_service.create_bill_splits(bill.id, splits)
    
    # Verify splits created correctly
    bill_splits = await bill_service.get_splits_for_bill(bill.id)
    
    # Should have 3 splits (2 explicit + 1 for primary account)
    assert len(bill_splits) == 3
    
    # Verify primary account split was calculated correctly
    primary_split = next(
        (split for split in bill_splits if split.account_id == checking.id),
        None
    )
    assert primary_split is not None
    assert primary_split.amount == Decimal("500.00")  # 1200 - 400 - 300
    
    # Test split validation - total exceeds bill amount
    excessive_splits = [
        {"account_id": savings.id, "amount": Decimal("700.00")},
        {"account_id": credit.id, "amount": Decimal("600.00")}
    ]
    
    with pytest.raises(ValueError) as excinfo:
        await bill_service.create_bill_splits(bill.id, excessive_splits)
    
    assert "exceed bill amount" in str(excinfo.value).lower()
```

### 3. Repository Integration

Test that services interact correctly with repositories:

```python
async def test_account_service_find_accounts_by_type(account_service, db_session):
    """Test finding accounts by type using repository layer."""
    # Create test accounts
    checking1 = await create_test_checking_account(db_session, name="Checking 1")
    checking2 = await create_test_checking_account(db_session, name="Checking 2")
    savings = await create_test_savings_account(db_session, name="Savings")
    
    # Test repository integration
    checking_accounts = await account_service.find_accounts_by_type("checking")
    
    assert len(checking_accounts) == 2
    account_names = [a.name for a in checking_accounts]
    assert "Checking 1" in account_names
    assert "Checking 2" in account_names
    assert "Savings" not in account_names
    
    # Test using repository through service
    all_accounts = await account_service.get_all_accounts()
    assert len(all_accounts) == 3
```

### 4. Cross-Entity Operations

Test operations that span multiple entity types:

```python
async def test_payment_service_create_payment(payment_service, db_session):
    """Test creating payment that affects multiple entities."""
    # Create test data
    account = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    bill = await create_test_bill(
        db_session, 
        amount=Decimal("200.00"),
        primary_account_id=account.id
    )
    
    # Perform cross-entity operation
    payment = await payment_service.create_payment(
        bill_id=bill.id,
        account_id=account.id,
        amount=Decimal("200.00"),
        payment_date=naive_utc_now()
    )
    
    # Verify payment created
    assert payment.id is not None
    assert payment.amount == Decimal("200.00")
    assert payment.bill_id == bill.id
    assert payment.status == "COMPLETED"
    
    # Verify bill updated
    updated_bill = await payment_service.bill_repository.get_by_id(bill.id)
    assert updated_bill.is_paid is True
    assert updated_bill.last_payment_date is not None
    
    # Verify account updated
    updated_account = await payment_service.account_repository.get_by_id(account.id)
    assert updated_account.available_balance == Decimal("800.00")  # 1000 - 200
    assert updated_account.current_balance == Decimal("800.00")  # 1000 - 200
```

### 5. Validation Logic

Test service-level validation:

```python
async def test_payment_service_validate_payment_amount(payment_service, db_session):
    """Test validation of payment amounts."""
    # Create test data
    bill = await create_test_bill(db_session, amount=Decimal("100.00"))
    account = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("50.00")
    )
    
    # Test validation - payment amount exceeds available balance
    from src.errors.account_errors import InsufficientFundsError
    
    with pytest.raises(InsufficientFundsError):
        await payment_service.create_payment(
            bill_id=bill.id,
            account_id=account.id,
            amount=Decimal("75.00"),  # Exceeds available balance
            payment_date=naive_utc_now()
        )
    
    # Test validation - negative payment amount
    with pytest.raises(ValueError):
        await payment_service.create_payment(
            bill_id=bill.id,
            account_id=account.id,
            amount=Decimal("-10.00"),  # Negative amount
            payment_date=naive_utc_now()
        )
```

### 6. Error Handling

Test error handling in services:

```python
async def test_account_service_error_handling(account_service):
    """Test handling of non-existent account."""
    # Test with non-existent ID
    from src.errors.account_errors import AccountNotFoundError
    
    with pytest.raises(AccountNotFoundError) as excinfo:
        await account_service.get_account_by_id(999999)
    
    # Error should include ID
    assert "999999" in str(excinfo.value)
    
    # Test with invalid UUID
    import uuid
    invalid_uuid = uuid.uuid4()
    with pytest.raises(AccountNotFoundError):
        await account_service.get_account_by_id(str(invalid_uuid))
```

### 7. Polymorphic Type Handling

Test handling of polymorphic account types:

```python
async def test_account_service_polymorphic_operations(account_service, db_session):
    """Test operations with polymorphic account types."""
    # Create different account types
    checking = await create_test_checking_account(db_session)
    credit = await create_test_credit_account(db_session)
    
    # Retrieve accounts with base service
    accounts = await account_service.get_all_accounts()
    
    # Verify correct types returned
    checking_account = next(a for a in accounts if a.id == checking.id)
    credit_account = next(a for a in accounts if a.id == credit.id)
    
    assert checking_account.account_type == "checking"
    assert credit_account.account_type == "credit"
    
    # Verify type-specific attributes accessible
    assert hasattr(checking_account, "overdraft_limit")
    assert hasattr(credit_account, "credit_limit")
    
    # Test type-specific operations
    account_detail = await account_service.get_account_details(checking.id)
    assert account_detail.account_type == "checking"
    
    # Test converting to response schema (should use correct subclass)
    response = account_service.to_response(checking_account)
    assert response.account_type == "checking"
    assert hasattr(response, "overdraft_limit")
```

### 8. Feature Flag Integration

Test feature flag integration in services:

```python
async def test_account_service_feature_flag_integration(
    db_session, feature_flag_service
):
    """Test feature flag integration in account service."""
    # Create service with feature flags
    from src.repositories.account_repository import AccountRepository
    from src.services.account_service import AccountService
    
    account_repository = AccountRepository(db_session)
    account_service = AccountService(
        account_repository=account_repository,
        feature_flag_service=feature_flag_service
    )
    
    # Enable test feature flag
    feature_flag_service.enable_flag("ENABLE_SAVINGS_INTEREST")
    
    # Create savings account
    savings = await create_test_savings_account(
        db_session, 
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        interest_rate=Decimal("0.03")  # 3% interest
    )
    
    # Test feature flag-controlled functionality
    interest = await account_service.calculate_monthly_interest(savings.id)
    assert interest == Decimal("2.50")  # (1000 * 0.03) / 12
    
    # Disable feature flag
    feature_flag_service.disable_flag("ENABLE_SAVINGS_INTEREST")
    
    # Test that feature is disabled
    from src.errors.feature_flag_errors import FeatureNotEnabledError
    
    with pytest.raises(FeatureNotEnabledError):
        await account_service.calculate_monthly_interest(savings.id)
```

### 9. Complex Business Rules

Test complex business rules spanning multiple entities:

```python
async def test_cashflow_service_forecast(cashflow_service, db_session):
    """Test cashflow forecasting with complex business rules."""
    # Create test data
    checking = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("500.00"),
        current_balance=Decimal("500.00")
    )
    
    # Create recurring bills
    for i in range(3):
        await create_test_bill(
            db_session,
            name=f"Bill {i}",
            amount=Decimal(f"{(i+1)*100}.00"),
            due_day=10+i,
            primary_account_id=checking.id
        )
    
    # Create future income
    from src.utils.datetime_utils import naive_days_from_now
    income_date = naive_days_from_now(15)
    await create_test_income(
        db_session,
        amount=Decimal("1000.00"),
        deposit_date=income_date,
        target_account_id=checking.id
    )
    
    # Calculate 30-day forecast
    forecast = await cashflow_service.calculate_30_day_forecast(checking.id)
    
    # Complex business rule assertions
    assert forecast.starting_balance == Decimal("500.00")
    assert forecast.total_expenses == Decimal("600.00")  # 100 + 200 + 300
    assert forecast.total_income == Decimal("1000.00")
    assert forecast.ending_balance == Decimal("900.00")  # 500 - 600 + 1000
    assert forecast.lowest_balance == Decimal("100.00")  # After first two bills, before income
    
    # Lowest balance should occur before income deposit
    lowest_date = forecast.lowest_balance_date
    assert lowest_date < income_date.date()
```

### 10. Specialized Account Type Services

Test specialized service implementations for different account types:

```python
async def test_bnpl_service_status_transitions(bnpl_service, db_session):
    """Test BNPL account status transition business rules."""
    # Create BNPL account
    bnpl = await create_test_bnpl_account(
        db_session,
        status="ACTIVE",
        current_balance=Decimal("1200.00"),
        payment_amount=Decimal("100.00"),
        payments_remaining=12
    )
    
    # Test transition to PAID_OFF
    await bnpl_service.mark_as_paid(bnpl.id)
    
    # Verify status updated correctly
    updated_bnpl = await bnpl_service.get_by_id(bnpl.id)
    assert updated_bnpl.status == "PAID_OFF"
    assert updated_bnpl.is_active is False
    assert updated_bnpl.current_balance == Decimal("0.00")
    assert updated_bnpl.payments_remaining == 0
    
    # Test transition to DEFAULTED
    bnpl = await create_test_bnpl_account(
        db_session,
        status="ACTIVE",
        current_balance=Decimal("1200.00")
    )
    
    await bnpl_service.mark_as_defaulted(bnpl.id)
    
    # Verify status updated correctly
    updated_bnpl = await bnpl_service.get_by_id(bnpl.id)
    assert updated_bnpl.status == "DEFAULTED"
    assert updated_bnpl.is_active is False
    
    # Test invalid transition
    bnpl = await create_test_bnpl_account(
        db_session,
        status="PAID_OFF",
        current_balance=Decimal("0.00")
    )
    
    # Cannot transition from PAID_OFF to DEFAULTED
    with pytest.raises(ValueError) as excinfo:
        await bnpl_service.mark_as_defaulted(bnpl.id)
    
    assert "invalid status transition" in str(excinfo.value).lower()
```

## Testing Repository Factory Integration

Debtonator uses a repository factory pattern, which should be tested:

```python
async def test_service_repository_factory_integration(db_session):
    """Test service integration with repository factory."""
    from src.factories.repository_factory import RepositoryFactory
    from src.services.account_service import AccountService
    
    # Create repository factory
    repo_factory = RepositoryFactory(db_session)
    
    # Create service with factory
    account_service = AccountService(
        account_repository=repo_factory.create_account_repository()
    )
    
    # Create test account
    account = await create_test_checking_account(db_session)
    
    # Test service operation
    result = await account_service.get_account_by_id(account.id)
    assert result.id == account.id
```

## Testing Dynamic Module Loading

Test dynamic module loading for account type operations:

```python
async def test_service_dynamic_module_loading(db_session):
    """Test service integration with dynamic module loading."""
    from src.registry.account_type_registry import AccountTypeRegistry
    from src.services.account_service import AccountService
    from src.repositories.account_repository import AccountRepository
    
    # Create registry with module mapping
    registry = AccountTypeRegistry()
    registry.register("checking", {
        "module": "banking.checking",
        "operations": ["deposit", "withdraw"]
    })
    
    # Create service with registry
    account_service = AccountService(
        account_repository=AccountRepository(db_session),
        account_type_registry=registry
    )
    
    # Create test account
    account = await create_test_checking_account(db_session)
    
    # Test dynamic operation
    await account_service.perform_account_operation(
        account_id=account.id,
        operation="deposit",
        amount=Decimal("100.00")
    )
    
    # Verify operation worked
    updated_account = await account_service.get_account_by_id(account.id)
    assert updated_account.available_balance == Decimal("1100.00")  # Initial + 100
```

## Testing Transaction Boundaries

Test that service methods properly handle transactions:

```python
async def test_service_transaction_boundaries(db_session):
    """Test transaction handling in services."""
    from src.services.payment_service import PaymentService
    from src.repositories.payment_repository import PaymentRepository
    from src.repositories.account_repository import AccountRepository
    from src.repositories.bill_repository import BillRepository
    
    # Create service with repositories
    payment_service = PaymentService(
        payment_repository=PaymentRepository(db_session),
        account_repository=AccountRepository(db_session),
        bill_repository=BillRepository(db_session)
    )
    
    # Create test data
    account = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    bill = await create_test_bill(
        db_session, 
        amount=Decimal("500.00"),
        primary_account_id=account.id
    )
    
    # Test transaction that should succeed
    payment = await payment_service.create_payment(
        bill_id=bill.id,
        account_id=account.id,
        amount=Decimal("500.00"),
        payment_date=naive_utc_now()
    )
    
    assert payment.id is not None
    assert payment.amount == Decimal("500.00")
    
    # Get updated account balance
    updated_account = await payment_service.account_repository.get_by_id(account.id)
    assert updated_account.available_balance == Decimal("500.00")  # 1000 - 500
    
    # Test transaction that should fail
    from src.errors.account_errors import InsufficientFundsError
    
    with pytest.raises(InsufficientFundsError):
        # Try to pay more than available balance
        await payment_service.create_payment(
            bill_id=bill.id,
            account_id=account.id,
            amount=Decimal("600.00")  # Exceeds available balance
        )
    
    # Verify transaction was rolled back
    account_after_error = await payment_service.account_repository.get_by_id(account.id)
    assert account_after_error.available_balance == Decimal("500.00")  # Unchanged
```

## Testing UTC Datetime Compliance (ADR-011)

Test proper handling of UTC datetimes in services:

```python
async def test_service_utc_datetime_compliance(bill_service, db_session):
    """Test UTC datetime compliance in services."""
    from src.utils.datetime_utils import utc_now, days_ago, days_from_now
    
    # Create bill with due date
    due_date = naive_days_from_now(10)  # Naive UTC for database
    bill = await create_test_bill(
        db_session,
        name="Test Bill",
        due_date=due_date
    )
    
    # Test timezone-aware datetime handling in service
    upcoming_bills = await bill_service.get_upcoming_bills(
        days=15  # Should include our bill
    )
    
    assert len(upcoming_bills) == 1
    assert upcoming_bills[0].id == bill.id
    
    # Create bill with past due date
    past_due_date = naive_days_ago(5)  # Naive UTC for database
    past_bill = await create_test_bill(
        db_session,
        name="Past Bill",
        due_date=past_due_date
    )
    
    # Test datetime comparison using timezone-aware datetimes
    overdue_bills = await bill_service.get_overdue_bills()
    
    assert len(overdue_bills) == 1
    assert overdue_bills[0].id == past_bill.id
```

## Testing Error Translation

Test that services translate repository errors appropriately:

```python
async def test_service_error_translation(account_service, db_session):
    """Test error translation in services."""
    # Create SQLAlchemy error (manually in this case)
    from sqlalchemy.exc import IntegrityError
    
    # Replace the get_by_id method to raise an IntegrityError
    original_method = account_service.account_repository.get_by_id
    
    async def mock_get_by_id(id):
        raise IntegrityError("Mock error", None, None)
    
    account_service.account_repository.get_by_id = mock_get_by_id
    
    try:
        # Service should translate SQLAlchemy error to domain error
        from src.errors.database_errors import DatabaseIntegrityError
        
        with pytest.raises(DatabaseIntegrityError):
            await account_service.get_account_by_id(1)
    finally:
        # Restore original method
        account_service.account_repository.get_by_id = original_method
```

## Best Practices

1. **Use Real Repositories**: Follow ADR-014 by using real repositories instead of mocks
2. **Proper Dependency Injection**: Inject dependencies through constructor parameters
3. **Test Business Rules**: Focus on testing business rules and service-specific logic
4. **Test Error Handling**: Verify that services handle errors appropriately
5. **Test Transaction Boundaries**: Verify that transactions are properly managed
6. **Follow UTC Datetime Compliance**: Use proper timezone-aware datetime functions
7. **Test Feature Flag Integration**: Verify feature flag integration when applicable
8. **Test Authorization Logic**: Verify that authorization checks work correctly
9. **Test Complex Business Rules**: Test complex rules spanning multiple entities
10. **Test Polymorphic Operations**: Verify handling of polymorphic types
11. **Thorough Financial Testing**: Test financial calculations with precise Decimal values
12. **Bill Split Testing**: Test bill splitting functionality thoroughly
13. **Repository Factory Testing**: Test integration with repository factory
14. **Cross-Entity Testing**: Test operations that affect multiple entities
15. **Comprehensive Error Testing**: Test all error conditions and their handling

## Common Anti-Patterns to Avoid

1. **Direct Database Access**: Services should use repositories, not direct DB access
2. **Mocking Repositories**: Follow ADR-014 by using real repositories, not mocks
3. **Testing Repository Implementation**: Focus on service logic, not repository details
4. **Testing Framework Behavior**: Test your service code, not the framework
5. **Missing Transaction Tests**: Don't forget to test transaction boundaries
6. **Hardcoded IDs**: Avoid hardcoded IDs in tests
7. **Naive Datetimes**: Use timezone-aware datetime functions from src/utils/datetime_utils.py
8. **Complex Service Dependencies**: Keep service dependencies manageable
9. **Circular Dependencies**: Avoid circular dependencies between services
10. **Missing Validation Tests**: Don't forget to test validation logic
11. **Skipping Polymorphic Testing**: Test all account types, not just the base ones
12. **Using Float for Money**: Always use Decimal for financial values
13. **Incomplete Error Testing**: Test all error conditions systematically
14. **Business Logic in Repositories**: Business logic belongs in services, not repositories
15. **Relying on Default Values**: Test services with specific values, not defaults

## Example Test File Structure

```python
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account_service import AccountService
from src.repositories.account_repository import AccountRepository
from src.errors.account_errors import AccountNotFoundError, InsufficientFundsError
from tests.fixtures.models.fixture_accounts_models import (
    create_test_checking_account,
    create_test_savings_account,
    create_test_credit_account
)
from src.utils.datetime_utils import naive_utc_now, naive_days_ago, naive_days_from_now

# Repository fixture
@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession):
    """Create an account repository for testing."""
    return AccountRepository(db_session)

# Service fixture
@pytest_asyncio.fixture
async def account_service(account_repository):
    """Create an account service for testing."""
    return AccountService(account_repository)

# Basic service tests
async def test_account_service_get_by_id(account_service, db_session):
    """Test retrieving account by ID."""
    # Test implementation...

# Business logic tests
async def test_account_service_calculate_balance(account_service, db_session):
    """Test balance calculation business logic."""
    # Test implementation...

# Error handling tests
async def test_account_service_handle_errors(account_service, db_session):
    """Test error handling in account service."""
    # Test implementation...

# Complex business rule tests
async def test_account_service_complex_business_rules(account_service, db_session):
    """Test complex business rules in account service."""
    # Test implementation...

# Polymorphic type tests
async def test_account_service_polymorphic_types(account_service, db_session):
    """Test handling of polymorphic account types."""
    # Test implementation...

# Feature flag tests
async def test_account_service_feature_flags(account_service, feature_flag_service, db_session):
    """Test feature flag integration in account service."""
    # Test implementation...
```
