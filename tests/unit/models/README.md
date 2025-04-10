# Unit Tests for SQLAlchemy Models

This directory contains unit tests for SQLAlchemy models used throughout the Debtonator application. These tests verify model behavior, relationships, constraints, and properties without crossing into repository or service layer functionality.

## Focus Areas

Model unit tests should focus on:

1. **Model Instantiation**: Creating models with valid attributes
2. **Model Relationships**: Testing relationships between models
3. **Model Properties**: Testing calculated properties and methods
4. **Database Constraints**: Testing database-level constraints
5. **Polymorphic Identity**: Testing polymorphic model behavior

## Example Test Case

```python
async def test_checking_account_creation(db_session):
    """Test creating a checking account with valid attributes."""
    checking = CheckingAccount(
        name="Primary Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        overdraft_limit=Decimal("100.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking)
    await db_session.flush()
    
    assert checking.id is not None
    assert checking.name == "Primary Checking"
    assert checking.available_balance == Decimal("1000.00")
    assert checking.account_type == "checking"  # Set by polymorphic identity
```

## SQLAlchemy 2.0 Pattern

Always use SQLAlchemy 2.0 syntax in tests:

```python
# ✅ Correct: Modern SQLAlchemy 2.0 async pattern
from sqlalchemy import select
stmt = select(Account).where(Account.id == some_id)
result = await db_session.execute(stmt)
item = result.scalars().first()

# ❌ Incorrect: Legacy pattern (will fail with AsyncSession)
items = db_session.query(Account).all()
```

## UTC Datetime Compliance (ADR-011)

Always follow ADR-011 for datetime handling:

```python
from src.utils.datetime_utils import naive_utc_now, naive_days_ago

# Use naive_utc_now() for database fields
model = StatementHistory(
    account_id=account.id,
    statement_date=naive_utc_now(),
    statement_balance=Decimal("500.00")
)
```

## Writing Model Tests

1. **Focus on model behavior**: Test model properties, methods, and constraints
2. **Don't test repository or service logic**: Keep tests focused on the model layer
3. **Use real database session**: All tests use a real SQLite database via the `db_session` fixture
4. **Use `flush()` not `commit()`**: Use `await db_session.flush()` instead of committing
5. **Use descriptive test names**: Names should clearly indicate what's being tested

## Test Organization

Tests are organized to mirror the structure of the `src/models` directory:

```
models/
├── test_accounts.py
├── test_bills.py
└── account_types/
    └── banking/
        ├── test_checking.py
        ├── test_savings.py
        └── test_credit.py
```
