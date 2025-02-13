import pytest
from decimal import Decimal
from datetime import date

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.services.bill_splits import BillSplitService, BillSplitValidationError
from src.schemas.bill_splits import BillSplitCreate, BillSplitValidation

@pytest.fixture(scope="function")
async def checking_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def credit_account(db_session):
    account = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.flush()
    return account

@pytest.fixture(scope="function")
async def liability(db_session):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("300.00"),
        due_date=date.today(),
        category_id=1,  # Assuming category 1 exists
        primary_account_id=1,  # Will be updated in tests
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(liability)
    await db_session.flush()
    return liability

async def test_create_bill_split_success(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=checking_account.id,
        amount=Decimal("100.00")
    )
    
    result = await service.create_bill_split(split)
    assert result.amount == Decimal("100.00")
    assert result.liability_id == liability.id
    assert result.account_id == checking_account.id

async def test_create_bill_split_insufficient_balance(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=checking_account.id,
        amount=Decimal("2000.00")  # More than available balance
    )
    
    with pytest.raises(BillSplitValidationError) as exc:
        await service.create_bill_split(split)
    assert "insufficient balance" in str(exc.value)

async def test_create_bill_split_insufficient_credit(db_session, credit_account, liability):
    service = BillSplitService(db_session)
    # Available credit is 1500 (2000 limit - 500 used)
    split = BillSplitCreate(
        liability_id=liability.id,
        account_id=credit_account.id,
        amount=Decimal("1600.00")  # More than available credit
    )
    
    with pytest.raises(BillSplitValidationError) as exc:
        await service.create_bill_split(split)
    assert "insufficient credit" in str(exc.value)

async def test_validate_splits_success(db_session, checking_account, credit_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("200.00")
            ),
            BillSplitCreate(
                liability_id=liability.id,
                account_id=credit_account.id,
                amount=Decimal("100.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is True
    assert error is None

async def test_validate_splits_total_mismatch(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=Decimal("400.00"),  # Different from liability amount
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("400.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "does not match liability amount" in error

async def test_validate_splits_duplicate_accounts(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("150.00")
            ),
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,  # Same account
                amount=Decimal("150.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "Duplicate accounts" in error

async def test_validate_splits_nonexistent_account(db_session, liability):
    service = BillSplitService(db_session)
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=99999,  # Non-existent account
                amount=Decimal("300.00")
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "Accounts not found" in error

async def test_validate_splits_insufficient_funds(db_session, checking_account, liability):
    service = BillSplitService(db_session)
    
    # Update liability amount to test insufficient funds
    liability.amount = Decimal("2000.00")
    await db_session.flush()
    
    validation = BillSplitValidation(
        liability_id=liability.id,
        total_amount=liability.amount,  # Now matches the split amount
        splits=[
            BillSplitCreate(
                liability_id=liability.id,
                account_id=checking_account.id,
                amount=Decimal("2000.00")  # More than available balance (1000.00)
            )
        ]
    )
    
    is_valid, error = await service.validate_splits(validation)
    assert is_valid is False
    assert "insufficient balance" in error
