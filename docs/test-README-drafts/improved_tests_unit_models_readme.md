# Unit Tests for SQLAlchemy Models

This directory contains unit tests for SQLAlchemy models used throughout the Debtonator application. These tests validate model behavior, relationships, constraints, and properties without crossing into repository or service layer functionality.

## Directory Structure

The model tests directory structure mirrors the structure of the `src/models` directory:

```
unit/models/
├── __init__.py
├── test_accounts.py
├── test_balance.py
├── test_bills.py
├── test_cashflow.py
├── test_income.py
├── test_payments.py
├── test_categories.py
├── ...
└── account_types/
    ├── __init__.py
    ├── banking/
    │   ├── __init__.py
    │   ├── test_checking.py
    │   ├── test_savings.py
    │   ├── test_credit.py
    │   ├── test_bnpl.py
    │   └── ...
    ├── bill/
    ├── investment/
    └── loan/
```

## Naming Convention

All test files follow a consistent naming convention:

- Files must start with the prefix `test_`
- The remainder should match the name of the file in `src/models` being tested
- Example: `src/models/accounts.py` → `test_accounts.py`

## Model Testing Focus Areas

Model unit tests should focus on:

### 1. Model Instantiation

Test that models can be created with valid attributes:

```python
async def test_checking_account_creation(db_session):
    """Test that a checking account can be created with valid attributes."""
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
    assert checking.current_balance == Decimal("1000.00")
    assert checking.overdraft_limit == Decimal("100.00")
    assert checking.account_type == "checking"  # Set by polymorphic identity
```

### 2. Model Relationships

Test one-to-many, many-to-one, and many-to-many relationships:

```python
async def test_account_bill_relationship(db_session):
    """Test that accounts have a relationship with bills."""
    # Create an account
    account = CheckingAccount(
        name="Bill Payment Account", 
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    
    # Create bills associated with the account
    bills = []
    for i in range(3):
        bill = Liability(
            name=f"Utility Bill {i}",
            amount=Decimal(f"{(i+1)*100}.00"),
            due_day=i+5,
            primary_account_id=account.id
        )
        db_session.add(bill)
        bills.append(bill)
    
    await db_session.flush()
    
    # Refresh the account to load relationships
    await db_session.refresh(account)
    
    # Test the relationship
    assert len(account.bills) == 3
    assert account.bills[0].name == "Utility Bill 0"
    assert account.bills[1].name == "Utility Bill 1"
    assert account.bills[2].name == "Utility Bill 2"
    
    # Test the inverse relationship
    for bill in bills:
        await db_session.refresh(bill)
        assert bill.primary_account.id == account.id
        assert bill.primary_account.name == "Bill Payment Account"
```

### 3. Bill Split Functionality

Test bill split relationships and automatic split creation:

```python
async def test_bill_split_relationships(db_session):
    """Test bill splits across multiple accounts."""
    # Create accounts
    checking = CheckingAccount(
        name="Primary Checking", 
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    savings = SavingsAccount(
        name="Savings Account", 
        available_balance=Decimal("5000.00"),
        current_balance=Decimal("5000.00")
    )
    db_session.add_all([checking, savings])
    await db_session.flush()
    
    # Create bill with primary account
    bill = Liability(
        name="Rent",
        amount=Decimal("1200.00"),
        due_day=1,
        primary_account_id=checking.id
    )
    db_session.add(bill)
    await db_session.flush()
    
    # Create explicit split for savings account
    savings_split = BillSplit(
        bill_id=bill.id,
        account_id=savings.id,
        amount=Decimal("800.00")  # Partial split
    )
    db_session.add(savings_split)
    await db_session.flush()
    
    # A primary account split should be created automatically
    from sqlalchemy import select
    stmt = select(BillSplit).where(
        (BillSplit.bill_id == bill.id) & 
        (BillSplit.account_id == checking.id)
    )
    result = await db_session.execute(stmt)
    primary_split = result.scalars().first()
    
    # Verify primary account split
    assert primary_split is not None
    assert primary_split.amount == Decimal("400.00")  # 1200 - 800
    
    # Verify relationships
    await db_session.refresh(bill)
    assert len(bill.splits) == 2
    split_amounts = [split.amount for split in bill.splits]
    assert Decimal("800.00") in split_amounts
    assert Decimal("400.00") in split_amounts
    
    # Verify split total equals bill amount
    split_total = sum(split.amount for split in bill.splits)
    assert split_total == bill.amount
```

### 4. Model Properties and Methods

Test properties, property setters, and methods on model instances:

```python
async def test_credit_account_available_credit(db_session):
    """Test the available_credit property on CreditAccount."""
    # Create a credit account
    credit = CreditAccount(
        name="Credit Card",
        credit_limit=Decimal("2000.00"),
        current_balance=Decimal("500.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(credit)
    await db_session.flush()
    
    # Test the property
    assert credit.available_credit == Decimal("1500.00")  # 2000 - 500
    
    # Test the property after changing current_balance
    credit.current_balance = Decimal("800.00")
    await db_session.flush()
    assert credit.available_credit == Decimal("1200.00")  # 2000 - 800
    
    # Test the property after changing credit_limit
    credit.credit_limit = Decimal("2500.00")
    await db_session.flush()
    assert credit.available_credit == Decimal("1700.00")  # 2500 - 800
```

### 5. Model Constraints

Test database constraints enforced by SQLAlchemy:

```python
async def test_account_name_uniqueness(db_session):
    """Test that account names must be unique."""
    # Create first account
    account1 = CheckingAccount(
        name="Duplicate Name Test",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    db_session.add(account1)
    await db_session.flush()
    
    # Create second account with same name
    account2 = SavingsAccount(
        name="Duplicate Name Test",  # Same name
        available_balance=Decimal("2000.00"),
        current_balance=Decimal("2000.00")
    )
    db_session.add(account2)
    
    # Should raise an IntegrityError
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.flush()
```

### 6. Polymorphic Account Types

Test polymorphic model behavior for all account types:

```python
async def test_polymorphic_account_query(db_session):
    """Test querying polymorphic account models."""
    # Create various account types
    checking = CheckingAccount(
        name="Primary Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        overdraft_limit=Decimal("200.00"),
    )
    savings = SavingsAccount(
        name="Emergency Savings",
        available_balance=Decimal("5000.00"),
        current_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.02"),  # 2% interest
    )
    credit = CreditAccount(
        name="Rewards Credit Card", 
        current_balance=Decimal("500.00"),
        credit_limit=Decimal("2500.00"),
    )
    bnpl = BNPLAccount(
        name="Buy Now Pay Later",
        current_balance=Decimal("300.00"),
        credit_limit=Decimal("1000.00"),
        payment_schedule="MONTHLY",
    )
    
    db_session.add_all([checking, savings, credit, bnpl])
    await db_session.flush()
    
    # Query using base class
    from sqlalchemy import select
    from src.models.accounts import Account
    
    stmt = select(Account).order_by(Account.name)
    result = await db_session.execute(stmt)
    accounts = result.scalars().all()
    
    # Verify polymorphic loading
    assert len(accounts) == 4
    
    # Verify correct types
    assert isinstance(accounts[0], BNPLAccount)
    assert isinstance(accounts[1], CheckingAccount)
    assert isinstance(accounts[2], SavingsAccount)
    assert isinstance(accounts[3], CreditAccount)
    
    # Verify type-specific properties
    assert accounts[1].overdraft_limit == Decimal("200.00")
    assert accounts[2].interest_rate == Decimal("0.02")
    assert accounts[3].available_credit == Decimal("2000.00")  # 2500 - 500
    assert accounts[0].payment_schedule == "MONTHLY"
```

### 7. BNPL Lifecycle Management

Test BNPL account lifecycle states:

```python
async def test_bnpl_account_lifecycle(db_session):
    """Test BNPL account lifecycle states."""
    # Create BNPL account in initial state
    bnpl = BNPLAccount(
        name="Furniture BNPL",
        current_balance=Decimal("1000.00"),
        credit_limit=Decimal("1000.00"),
        status="ACTIVE",
        payment_schedule="MONTHLY",
    )
    db_session.add(bnpl)
    await db_session.flush()
    
    # Test initial state
    assert bnpl.status == "ACTIVE"
    assert bnpl.is_active is True
    
    # Test transition to PAID_OFF
    bnpl.status = "PAID_OFF"
    await db_session.flush()
    assert bnpl.is_active is False
    
    # Test transition to DEFAULTED
    bnpl.status = "DEFAULTED"
    bnpl.current_balance = Decimal("500.00")  # Still has balance
    await db_session.flush()
    assert bnpl.is_active is False
    
    # Test invalid transition
    with pytest.raises(ValueError) as excinfo:
        bnpl.status = "INVALID_STATUS"
    
    assert "Invalid status" in str(excinfo.value)
```

### 8. DateTime Handling (Per ADR-011)

Test proper datetime handling for all model timestamps:

```python
async def test_model_datetime_fields(db_session):
    """Test datetime fields in models follow ADR-011."""
    from src.utils.datetime_utils import naive_utc_now, naive_days_ago, naive_days_from_now
    
    # Create account with specific created_at time
    created_time = naive_days_ago(5)  # 5 days ago
    account = CheckingAccount(
        name="DateTime Test Account",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        created_at=created_time,
        updated_at=naive_utc_now(),
    )
    db_session.add(account)
    await db_session.flush()
    
    # Create statement history with multiple dates
    statement1 = StatementHistory(
        account_id=account.id,
        statement_date=naive_days_ago(30),  # 30 days ago
        statement_balance=Decimal("1200.00"),
    )
    statement2 = StatementHistory(
        account_id=account.id,
        statement_date=naive_days_ago(15),  # 15 days ago
        statement_balance=Decimal("1100.00"),
    )
    db_session.add_all([statement1, statement2])
    await db_session.flush()
    
    # Query account to verify datetime storage
    from sqlalchemy import select
    stmt = select(CheckingAccount).where(CheckingAccount.id == account.id)
    result = await db_session.execute(stmt)
    fetched_account = result.scalars().first()
    
    # Verify datetimes stored correctly
    assert fetched_account.created_at == created_time
    
    # Verify statements stored correctly and are ordered correctly
    await db_session.refresh(account)
    assert len(account.statement_history) == 2
    assert account.statement_history[0].statement_date < account.statement_history[1].statement_date
```

### 9. Decimal Precision for Financial Calculations

Test decimal precision for monetary amounts:

```python
async def test_decimal_precision_for_financial_fields(db_session):
    """Test that decimal precision is maintained for financial fields."""
    # Create account with precise decimal values
    checking = CheckingAccount(
        name="Precision Test",
        available_balance=Decimal("1000.1234"),  # 4 decimal places
        current_balance=Decimal("1000.1234"),
        overdraft_limit=Decimal("100.5678")
    )
    db_session.add(checking)
    await db_session.flush()
    
    # Query to verify precision
    from sqlalchemy import select
    stmt = select(CheckingAccount).where(CheckingAccount.id == checking.id)
    result = await db_session.execute(stmt)
    fetched_account = result.scalars().first()
    
    # Verify precision is maintained in the database
    assert fetched_account.available_balance == Decimal("1000.1234")
    assert fetched_account.current_balance == Decimal("1000.1234")
    assert fetched_account.overdraft_limit == Decimal("100.5678")
    
    # Test calculations with precise decimals
    checking.available_balance += Decimal("0.0001")
    await db_session.flush()
    assert checking.available_balance == Decimal("1000.1235")
```

### 10. Default Values and Initialization Logic

Test that default values are properly set:

```python
async def test_account_default_values(db_session):
    """Test that default values are set correctly."""
    # Create account with minimal fields
    account = CheckingAccount(name="Default Values Test")
    
    # Defaults should be set
    assert account.available_balance == Decimal("0.00")
    assert account.current_balance == Decimal("0.00")
    assert account.overdraft_limit == Decimal("0.00")
    assert account.status == "ACTIVE"
    
    db_session.add(account)
    await db_session.flush()
    
    # created_at and updated_at should be set automatically
    assert account.created_at is not None
    assert account.updated_at is not None
    
    # created_at and updated_at should be naive UTC datetimes
    assert account.created_at.tzinfo is None  # Naive datetime
    assert account.updated_at.tzinfo is None  # Naive datetime
```

## Testing with a Real Database

All model tests use a real SQLite database through the `db_session` fixture. This aligns with our "Real Objects Testing Philosophy" from ADR-014.

### Key Guidelines:

1. **Use the db_session fixture**: Always pass the `db_session` fixture to your test function
2. **Flush, don't commit**: Use `await db_session.flush()` instead of `commit()`
3. **Refresh after operations**: Use `await db_session.refresh(model)` after changes that affect relationships
4. **Catch expected exceptions**: Use `pytest.raises()` for testing constraint violations
5. **Create test-specific instances**: Don't rely on test fixtures for models you'll modify

### Using Modern SQLAlchemy 2.0 Syntax

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

## Datetime Testing Requirements (ADR-011)

All datetime fields must comply with ADR-011 (UTC datetime handling):

1. **Use naive_utc_now() for database fields**: Database operations should use naive UTC datetimes
2. **Don't use datetime.now()**: Always use functions from `src/utils/datetime_utils.py`
3. **Test timezone handling**: Include tests for datetime field behavior

### Naive vs. Timezone-Aware Datetime Functions

Understanding which datetime function to use is critical:

| Function | Use Case | Example |
|----------|----------|---------|
| `naive_utc_now()` | Database field values | `created_at=naive_utc_now()` |
| `naive_days_ago(n)` | Past database dates | `statement_date=naive_days_ago(30)` |
| `naive_days_from_now(n)` | Future database dates | `due_date=naive_days_from_now(14)` |
| `utc_now()` | Business logic comparisons | `if timestamp > utc_now():` |
| `days_ago(n)` | Business logic past dates | `if timestamp < days_ago(7):` |
| `days_from_now(n)` | Business logic future dates | `if due_date <= days_from_now(30):` |

Example of proper datetime function usage:

```python
from src.utils.datetime_utils import naive_utc_now, naive_days_ago, utc_now, days_from_now

async def test_account_statement_datetime_handling(db_session):
    """Test proper datetime handling in statement histories."""
    # Create account
    account = CreditAccount(
        name="Credit Card",
        credit_limit=Decimal("2000.00"),
        current_balance=Decimal("500.00"),
        created_at=naive_utc_now(),
    )
    db_session.add(account)
    await db_session.flush()
    
    # Create statement with naive datetime (for database)
    statement_date = naive_days_ago(30)  # Naive UTC datetime (30 days ago)
    statement = StatementHistory(
        account_id=account.id,
        statement_date=statement_date,
        statement_balance=Decimal("450.00"),
        due_date=naive_days_from_now(15),  # Naive UTC datetime (15 days in future)
    )
    db_session.add(statement)
    await db_session.flush()
    
    # Test business logic with timezone-aware datetimes
    due_date_aware = days_from_now(15)  # Timezone-aware datetime
    
    # Calculate if statement is due soon (using business logic)
    is_due_soon = statement.is_due_soon(days_threshold=20)
    
    # This calculation should use timezone-aware datetimes
    assert is_due_soon is True
```

## Testing Patterns for Common Model Features

### Testing Bill Split Logic

Bill splitting is a core feature of Debtonator and requires thorough testing:

```python
async def test_bill_split_validation(db_session):
    """Test bill split validation logic."""
    # Create accounts
    checking = CheckingAccount(name="Checking", available_balance=Decimal("1000.00"))
    savings = SavingsAccount(name="Savings", available_balance=Decimal("2000.00"))
    credit = CreditAccount(name="Credit", credit_limit=Decimal("3000.00"))
    db_session.add_all([checking, savings, credit])
    await db_session.flush()
    
    # Create bill with primary account (checking)
    bill = Liability(
        name="Rent",
        amount=Decimal("1500.00"),
        due_day=1,
        primary_account_id=checking.id
    )
    db_session.add(bill)
    await db_session.flush()
    
    # Create splits for other accounts
    splits = [
        BillSplit(bill_id=bill.id, account_id=savings.id, amount=Decimal("500.00")),
        BillSplit(bill_id=bill.id, account_id=credit.id, amount=Decimal("200.00"))
    ]
    db_session.add_all(splits)
    await db_session.flush()
    
    # Verify primary account split is created automatically
    from sqlalchemy import select
    stmt = select(BillSplit).where(
        (BillSplit.bill_id == bill.id) & 
        (BillSplit.account_id == checking.id)
    )
    result = await db_session.execute(stmt)
    primary_split = result.scalars().first()
    
    # Validate amount is calculated correctly
    assert primary_split is not None
    assert primary_split.amount == Decimal("800.00")  # 1500 - 500 - 200
    
    # Test split validation - total exceeds bill amount
    excessive_split = BillSplit(
        bill_id=bill.id,
        account_id=savings.id,
        amount=Decimal("1000.00")  # Would make total exceed bill amount
    )
    db_session.add(excessive_split)
    
    # Should raise an IntegrityError or constraint violation
    from sqlalchemy.exc import IntegrityError
    with pytest.raises((IntegrityError, ValueError)):
        await db_session.flush()
```

### Testing Amount Fields with Decimal Precision

Financial applications require precise decimal handling:

```python
async def test_financial_decimal_precision(db_session):
    """Test decimal precision for financial calculations."""
    # Create account with precise decimal
    account = CheckingAccount(
        name="Precision Test",
        available_balance=Decimal("1000.1234"),  # 4 decimal places
        current_balance=Decimal("1000.1234")
    )
    db_session.add(account)
    await db_session.flush()
    
    # Test precise calculation
    original_balance = account.available_balance
    
    # Apply small interest calculation (2.5% APY, daily rate)
    daily_interest_rate = Decimal("0.025") / Decimal("365")
    daily_interest = account.available_balance * daily_interest_rate
    
    # Update balance with interest
    account.available_balance += daily_interest
    account.current_balance += daily_interest
    await db_session.flush()
    
    # Calculate expected result with full precision
    expected_balance = original_balance * (Decimal("1") + daily_interest_rate)
    
    # Verify precision is maintained throughout calculation
    assert account.available_balance == expected_balance
    
    # Query to verify
    from sqlalchemy import select
    stmt = select(CheckingAccount).where(CheckingAccount.id == account.id)
    result = await db_session.execute(stmt)
    fetched_account = result.scalars().first()
    
    # Verify precision persisted to database
    assert fetched_account.available_balance == expected_balance
```

### Testing Cascade Delete

Test the cascade delete behavior for related records:

```python
async def test_cascade_delete_for_accounts(db_session):
    """Test cascade delete behavior for accounts and related records."""
    # Create account
    account = CheckingAccount(
        name="Delete Test Account",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    
    # Create related records
    # 1. Statement history
    for i in range(3):
        statement = StatementHistory(
            account_id=account.id,
            statement_date=naive_days_ago(30 * (i+1)),
            statement_balance=Decimal(f"{1000 - i*100}.00")
        )
        db_session.add(statement)
    
    # 2. Bills with this account as primary
    for i in range(2):
        bill = Liability(
            name=f"Bill {i+1}",
            amount=Decimal(f"{(i+1)*100}.00"),
            due_day=i+1,
            primary_account_id=account.id
        )
        db_session.add(bill)
    
    await db_session.flush()
    await db_session.refresh(account)
    
    # Verify related records exist
    assert len(account.statement_history) == 3
    assert len(account.bills) == 2
    
    # Get IDs for later verification
    statement_ids = [s.id for s in account.statement_history]
    bill_ids = [b.id for b in account.bills]
    
    # Delete the account
    await db_session.delete(account)
    await db_session.flush()
    
    # Verify account is deleted
    from sqlalchemy import select
    stmt = select(CheckingAccount).where(CheckingAccount.id == account.id)
    result = await db_session.execute(stmt)
    deleted_account = result.scalars().first()
    assert deleted_account is None
    
    # Verify statement history is deleted (cascade)
    stmt = select(StatementHistory).where(StatementHistory.id.in_(statement_ids))
    result = await db_session.execute(stmt)
    remaining_statements = result.scalars().all()
    assert len(remaining_statements) == 0
    
    # Verify bills are NOT deleted (set null or protect)
    stmt = select(Liability).where(Liability.id.in_(bill_ids))
    result = await db_session.execute(stmt)
    remaining_bills = result.scalars().all()
    assert len(remaining_bills) == 2
    
    # Verify bills have null primary_account_id
    for bill in remaining_bills:
        assert bill.primary_account_id is None
```

## Testing Different Account Types

Debtonator supports multiple account types that must be thoroughly tested:

### Testing Checking Accounts

```python
async def test_checking_account_specific_features(db_session):
    """Test checking account specific features."""
    # Create checking account with overdraft
    checking = CheckingAccount(
        name="Checking with Overdraft",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        overdraft_limit=Decimal("200.00")
    )
    db_session.add(checking)
    await db_session.flush()
    
    # Test overdraft protection
    # Should allow withdrawal up to balance + overdraft limit
    max_withdrawal = checking.available_balance + checking.overdraft_limit
    
    # This should succeed (just at the limit)
    checking.available_balance -= max_withdrawal
    checking.current_balance -= max_withdrawal
    await db_session.flush()
    
    assert checking.available_balance == Decimal("-200.00")
    assert checking.current_balance == Decimal("-200.00")
    
    # Reset for next test
    checking.available_balance = Decimal("1000.00")
    checking.current_balance = Decimal("1000.00")
    await db_session.flush()
    
    # This should fail (exceeds overdraft limit)
    with pytest.raises(ValueError):
        checking.available_balance = Decimal("-201.00")  # Exceeds overdraft limit
```

### Testing Credit Accounts

```python
async def test_credit_account_specific_features(db_session):
    """Test credit account specific features."""
    # Create credit account
    credit = CreditAccount(
        name="Rewards Credit Card",
        credit_limit=Decimal("2000.00"),
        current_balance=Decimal("500.00"),
        available_credit=Decimal("1500.00")  # Calculated field
    )
    db_session.add(credit)
    await db_session.flush()
    
    # Test available_credit calculation
    assert credit.available_credit == Decimal("1500.00")  # credit_limit - current_balance
    
    # Test credit limit enforcement
    with pytest.raises(ValueError):
        credit.current_balance = Decimal("2100.00")  # Exceeds credit limit
    
    # Test payment processing
    # Make a payment
    payment_amount = Decimal("200.00")
    credit.current_balance -= payment_amount
    await db_session.flush()
    
    # Available credit should increase
    assert credit.current_balance == Decimal("300.00")
    assert credit.available_credit == Decimal("1700.00")
```

### Testing BNPL Accounts

```python
async def test_bnpl_account_specific_features(db_session):
    """Test Buy Now Pay Later account specific features."""
    # Create BNPL account
    bnpl = BNPLAccount(
        name="Furniture BNPL",
        credit_limit=Decimal("1200.00"),
        current_balance=Decimal("1200.00"),  # Fully utilized
        payment_schedule="MONTHLY",
        number_of_payments=12,
        status="ACTIVE"
    )
    db_session.add(bnpl)
    await db_session.flush()
    
    # Test payment tracking
    # Make a payment
    payment_amount = Decimal("100.00")  # Monthly payment
    bnpl.current_balance -= payment_amount
    bnpl.payments_made += 1
    await db_session.flush()
    
    assert bnpl.current_balance == Decimal("1100.00")
    assert bnpl.payments_made == 1
    assert bnpl.payments_remaining == 11
    
    # Test status transitions
    # Make full payment
    bnpl.current_balance = Decimal("0.00")
    bnpl.payments_made = 12
    bnpl.status = "PAID_OFF"
    await db_session.flush()
    
    assert bnpl.status == "PAID_OFF"
    assert bnpl.is_active is False
    
    # Test default transition
    bnpl.status = "DEFAULTED"
    await db_session.flush()
    
    assert bnpl.status == "DEFAULTED"
    assert bnpl.is_active is False
```

## Best Practices

1. **Test Layer Isolation**: Model tests should only test model functionality, not repository or service logic
2. **Test One Thing Per Test**: Each test should focus on a single behavior or feature
3. **Descriptive Test Names**: Use clear, descriptive names that indicate what's being tested
4. **Complete Test Coverage**: Test all model properties, methods, relationships, and constraints
5. **Test Edge Cases**: Include tests for boundary conditions and edge cases
6. **Avoid Direct Table Access**: Use the SQLAlchemy models, not direct table access
7. **Use Modern SQLAlchemy 2.0 Syntax**: Use `select()` instead of `query()`
8. **Proper UTC Datetime Handling**: Follow ADR-011 requirements for all datetime fields
9. **Independent Tests**: Each test should work independently of others
10. **No Complex Setup**: Keep test setup as simple as possible
11. **Test All Account Types**: Ensure coverage for all polymorphic account types
12. **Test Bill Split Logic**: Thoroughly test bill splitting functionality
13. **Test Decimal Precision**: Verify financial calculations maintain proper precision

## Common Anti-Patterns to Avoid

1. **Crossing Layer Boundaries**: Don't test repository or service logic in model tests
2. **Using Mocks**: Don't use unittest.mock or similar mocking libraries for model tests
3. **Testing SQLAlchemy Internals**: Test your model behavior, not SQLAlchemy's functionality
4. **Hardcoded IDs**: Don't use hardcoded IDs for relationships
5. **Naive Datetimes**: Don't use naive datetimes (except with naive_* utility functions)
6. **Complex Fixture Chains**: Avoid creating complex dependency chains between fixtures
7. **Testing Non-Database Properties**: Use regular unit tests for pure logic properties
8. **Direct datetime.now()**: Never use datetime.now() directly; use utility functions
9. **Missing Validation Tests**: Always test model constraints and validation rules
10. **Incomplete Polymorphic Testing**: Test all account types, not just the base ones

## Performance Considerations

Model tests can be resource-intensive. Follow these guidelines for better performance:

1. **Create Only What You Need**: Create only the model instances required for the test
2. **Batch Database Operations**: Use db_session.add_all() for multiple objects
3. **Minimize Session Flushes**: Flush once after creating all objects when possible
4. **Use In-Memory SQLite**: Tests should run against in-memory database for speed
5. **Clean Test Data**: Ensure tests don't leave data that affects other tests

## Example Test File Structure

```python
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.account_types.banking.checking import CheckingAccount
from src.models.bills import Liability
from src.models.bill_splits import BillSplit
from src.utils.datetime_utils import naive_utc_now, naive_days_ago

# Basic instantiation test
async def test_checking_account_creation(db_session: AsyncSession):
    """Test creating a checking account with valid attributes."""
    # Test implementation...

# Relationship tests
async def test_checking_account_bill_relationship(db_session: AsyncSession):
    """Test the relationship between checking account and bills."""
    # Test implementation...

# Property/method tests
async def test_checking_account_available_balance(db_session: AsyncSession):
    """Test the available_balance property behaves correctly."""
    # Test implementation...

# Constraint tests
async def test_checking_account_unique_constraints(db_session: AsyncSession):
    """Test uniqueness constraints on checking account."""
    # Test implementation...

# Default value tests
async def test_checking_account_default_values(db_session: AsyncSession):
    """Test default values are set correctly on checking account."""
    # Test implementation...

# Edge case tests
async def test_checking_account_zero_balance(db_session: AsyncSession):
    """Test checking account with zero balance."""
    # Test implementation...

# Bill split tests
async def test_checking_account_bill_splits(db_session: AsyncSession):
    """Test bill splitting functionality with checking account."""
    # Test implementation...
```