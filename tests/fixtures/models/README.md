# Test Fixtures for SQLAlchemy Models

This directory contains fixture functions for creating test instances of SQLAlchemy models used throughout the Debtonator application.

## Directory Structure

The fixtures directory mirrors the structure of the `src/models` directory:

```
fixtures/models/
├── __init__.py
├── fixture_accounts_models.py
├── fixture_balance_models.py
├── fixture_cashflow_models.py
├── ...
└── account_types/
    ├── __init__.py
    ├── banking/
    │   ├── __init__.py
    │   ├── fixture_checking_models.py
    │   ├── fixture_credit_models.py
    │   ├── ...
    ├── bill/
    ├── investment/
    └── loan/
```

For empty directories like `bill/`, `investment/`, and `loan/`, fixtures should be created proactively when the corresponding model files are added to those directories, following the same patterns established in this document.

## Naming Convention

All fixture files follow a consistent naming convention:

- Files must start with the prefix `fixture_`
- The middle part should match the name of the file in `src/models` the fixture represents
- Files should end with the suffix `_models`

For example:
- `src/models/accounts.py` → `fixture_accounts_models.py`
- `src/models/account_types/banking/checking.py` → `fixture_checking_models.py`

## Creating New Fixtures

When adding a new model to the codebase, follow these steps to create the corresponding fixture:

1. Create a new file with the appropriate naming convention in the corresponding location
2. Import the necessary model classes from `src/models/`
3. Import `pytest_asyncio` and the `AsyncSession` type
4. Create fixture functions that instantiate and return model instances
5. Register the new fixture file in `tests/conftest.py`
6. Create a simple test that uses the fixture to validate it works correctly

## Fixture Creation Guidelines

### Basic Rules

1. Use `@pytest_asyncio.fixture` for all fixture functions to ensure proper async support
2. Every SQLAlchemy model should have at least one corresponding fixture
3. Fixtures should only create model instances, not repositories or services (follow SRP)
4. Use `await db_session.flush()` and `await db_session.refresh(fixture)` instead of `commit()` where possible
5. Always use timezone-aware datetime functions from `src/utils/datetime_utils.py` (per ADR-011)
6. Include clear docstrings for each fixture function explaining its purpose

### Polymorphic Models

For polymorphic models (like account types):

1. Always use the proper subclass constructor that matches the intended polymorphic type:

```python
# ✅ Correct: Using concrete subclass constructor 
checking = CheckingAccount(
    name="Primary Checking",
    available_balance=Decimal("1000.00"),
    current_balance=Decimal("1000.00")
)

# ❌ Incorrect: Setting discriminator on base class
account = Account(
    name="Primary Checking",
    account_type="checking",  # Will cause SQLAlchemy polymorphic warnings
    available_balance=Decimal("1000.00"),
    current_balance=Decimal("1000.00")
)
```

2. Create dedicated fixtures for each polymorphic type with appropriate type-specific attributes

### Example Fixture

```python
from decimal import Decimal
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.utils.datetime_utils import naive_utc_now

@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """Primary Test Checking for use in various tests"""
    checking_account = CheckingAccount(
        name="Primary Test Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking_account)
    await db_session.flush()
    await db_session.refresh(checking_account)
    return checking_account
```

## Registration in conftest.py

All fixture files must be registered in the `pytest_plugins` list in `tests/conftest.py` to make them available across the test suite:

```python
pytest_plugins = [
    # ... other fixtures
    "tests.fixtures.models.fixture_accounts_models",
    "tests.fixtures.models.account_types.banking.fixture_checking_models",
    # ... more fixtures
]
```

## Complex Relationships

### One-to-Many Relationships

When creating fixtures for models with one-to-many relationships:

```python
@pytest_asyncio.fixture
async def test_category_with_bills(db_session: AsyncSession) -> Category:
    """Category with multiple bills attached"""
    category = Category(name="Test Category", category_type="EXPENSE")
    db_session.add(category)
    await db_session.flush()

    # Create multiple bills in this category
    for i in range(3):
        bill = Liability(
            name=f"Bill {i}",
            amount=Decimal(f"{(i+1)*100}.00"),
            due_day=i+1,
            category_id=category.id
        )
        db_session.add(bill)
    
    await db_session.flush()
    await db_session.refresh(category)
    return category
```

### Many-to-Many Relationships

For many-to-many relationships using association tables:

```python
@pytest_asyncio.fixture
async def test_payment_with_sources(db_session: AsyncSession) -> Payment:
    """Payment with multiple payment sources"""
    # Create accounts first
    accounts = []
    for i in range(3):
        account = CheckingAccount(
            name=f"Account {i}",
            available_balance=Decimal("1000.00"),
            current_balance=Decimal("1000.00")
        )
        db_session.add(account)
        accounts.append(account)
    
    await db_session.flush()
    
    # Create payment
    payment = Payment(
        amount=Decimal("300.00"),
        payment_date=naive_utc_now(),
        status="PENDING"
    )
    db_session.add(payment)
    await db_session.flush()
    
    # Create payment sources (association records)
    for i, account in enumerate(accounts):
        source = PaymentSource(
            payment_id=payment.id,
            account_id=account.id,
            amount=Decimal("100.00")  # Split evenly
        )
        db_session.add(source)
    
    await db_session.flush()
    await db_session.refresh(payment)
    return payment
```

### Handling Unique Constraints

For models with unique constraints, ensure test fixtures don't conflict:

```python
@pytest_asyncio.fixture
async def test_unique_account(db_session: AsyncSession) -> Account:
    """Account with a unique identifier"""
    # Use a UUID or timestamp to ensure uniqueness
    import uuid
    unique_id = str(uuid.uuid4())
    
    account = CheckingAccount(
        name=f"Unique Account {unique_id}",
        identifier=f"ACCT-{unique_id}",  # Unique field
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account
```

## Testing Edge Cases

Create fixtures that test error conditions:

```python
@pytest_asyncio.fixture
async def test_invalid_account(db_session: AsyncSession) -> CheckingAccount:
    """Account with invalid field combination to test validation"""
    # Create account that will fail certain validations
    account = CheckingAccount(
        name="Invalid Account",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("-500.00"),  # Negative balance
        overdraft_limit=Decimal("0.00")      # No overdraft allowed
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account
```

## Using Fixtures Effectively in Tests

### Isolation of Test Cases

To prevent test dependencies and ensure isolation:

```python
async def test_account_update(db_session: AsyncSession):
    """Test should create its own instance, not depend on a fixture"""
    # Create account specifically for this test
    account = CheckingAccount(
        name="Test-Specific Account",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    
    # Now perform the test operations
    account.available_balance = Decimal("1500.00")
    await db_session.flush()
    
    # Query to verify changes persisted
    from sqlalchemy import select
    stmt = select(CheckingAccount).where(CheckingAccount.id == account.id)
    result = await db_session.execute(stmt)
    updated_account = result.scalars().first()
    
    assert updated_account.available_balance == Decimal("1500.00")
```

### Testing Multiple Scenarios

When testing multiple scenarios, create specific fixtures for each case:

```python
@pytest_asyncio.fixture
async def test_low_balance_account(db_session: AsyncSession) -> CheckingAccount:
    """Account with low balance for testing warning scenarios"""
    # Implementation...

@pytest_asyncio.fixture
async def test_overdrafted_account(db_session: AsyncSession) -> CheckingAccount:
    """Account with negative balance for testing overdraft scenarios"""
    # Implementation...

@pytest_asyncio.fixture
async def test_high_balance_account(db_session: AsyncSession) -> CheckingAccount:
    """Account with high balance for testing interest scenarios"""
    # Implementation...
```

## Best Practices

1. **Comprehensive Coverage**: Create fixtures for every SQLAlchemy model in the codebase
2. **Minimal Dependencies**: Fixtures should create only what they need and avoid complex dependencies
3. **Realistic Data**: Use realistic test data with proper decimal precision and field types
4. **Clear Naming**: Use descriptive fixture function names (`test_checking_with_overdraft` vs `test_account2`)
5. **Variability**: Create multiple fixtures for complex models to cover different scenarios
6. **Reuse Prevention**: Create test-specific instances for tests that modify data
7. **UTC Compliance**: Follow ADR-011 by using `naive_utc_now()` or other timezone-aware datetime utilities
8. **Type Hinting**: Always include proper return type annotations on fixture functions
9. **Relationship Testing**: Create dedicated fixtures for testing complex relationships
10. **Edge Case Coverage**: Include fixtures for testing validation and error conditions

## Common Patterns

### Creating Multiple Related Instances

```python
@pytest_asyncio.fixture
async def test_multiple_accounts(db_session: AsyncSession) -> List[Account]:
    """Create multiple test accounts of different types."""
    accounts = []
    
    # Create instances
    checking = CheckingAccount(name="Checking A", available_balance=Decimal("1200.00"))
    db_session.add(checking)
    accounts.append(checking)
    
    savings = SavingsAccount(name="Savings B", available_balance=Decimal("5000.00"))
    db_session.add(savings)
    accounts.append(savings)
    
    # Flush to get IDs
    await db_session.flush()

    # Refresh all entries
    for account in accounts:
        await db_session.refresh(account)

    return accounts
```

### Specialized Variations

```python
@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """Basic checking account"""
    # ... standard implementation
    
@pytest_asyncio.fixture
async def test_checking_with_overdraft(db_session: AsyncSession) -> CheckingAccount:
    """Checking account with overdraft protection enabled"""
    # ... same model type with different attributes
```
