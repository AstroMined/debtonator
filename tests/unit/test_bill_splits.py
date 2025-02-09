import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models.bills import Bill
from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.services.bill_splits import validate_bill_splits, calculate_split_totals

@pytest.fixture
async def sample_accounts(setup_db, db_session):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(checking)
    db_session.add(credit)
    await db_session.commit()
    
    return {"checking": checking, "credit": credit}

@pytest.fixture
async def sample_bill(db_session, sample_accounts):
    bill = Bill(
        month="January",
        day_of_month=15,
        due_date=date(2025, 1, 15),
        bill_name="Test Bill",
        amount=Decimal("300.00"),
        account_id=sample_accounts["checking"].id,
        account_name=sample_accounts["checking"].name,  # Add account name
        auto_pay=False,
        paid=False
    )
    
    db_session.add(bill)
    await db_session.commit()
    return bill

@pytest.mark.asyncio
async def test_create_bill_split(setup_db, db_session, sample_bill, sample_accounts):
    # Create a bill split
    split = BillSplit(
        bill_id=sample_bill.id,
        account_id=sample_accounts["credit"].id,
        amount=Decimal("100.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(split)
    await db_session.commit()
    
    # Fetch and verify the split
    result = await db_session.execute(
        select(BillSplit).where(BillSplit.bill_id == sample_bill.id)
    )
    db_split = result.scalar_one()
    
    assert db_split.amount == Decimal("100.00")
    assert db_split.bill_id == sample_bill.id
    assert db_split.account_id == sample_accounts["credit"].id

@pytest.mark.asyncio
async def test_validate_bill_splits_total(setup_db, db_session, sample_bill, sample_accounts):
    # Create splits that sum to the bill amount
    splits = [
        BillSplit(
            bill_id=sample_bill.id,
            account_id=sample_accounts["checking"].id,
            amount=Decimal("200.00"),
            created_at=date.today(),
            updated_at=date.today()
        ),
        BillSplit(
            bill_id=sample_bill.id,
            account_id=sample_accounts["credit"].id,
            amount=Decimal("100.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    
    db_session.add_all(splits)
    await db_session.commit()
    
    # Validate splits
    total = await calculate_split_totals(db_session, sample_bill.id)
    assert total == sample_bill.amount
    
    is_valid = await validate_bill_splits(db_session, sample_bill.id)
    assert is_valid is True

@pytest.mark.asyncio
async def test_validate_bill_splits_invalid_total(setup_db, db_session, sample_bill, sample_accounts):
    # Create splits that don't sum to bill amount
    splits = [
        BillSplit(
            bill_id=sample_bill.id,
            account_id=sample_accounts["checking"].id,
            amount=Decimal("100.00"),
            created_at=date.today(),
            updated_at=date.today()
        ),
        BillSplit(
            bill_id=sample_bill.id,
            account_id=sample_accounts["credit"].id,
            amount=Decimal("100.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    
    db_session.add_all(splits)
    await db_session.commit()
    
    # Validate splits
    total = await calculate_split_totals(db_session, sample_bill.id)
    assert total == Decimal("200.00")  # Less than bill amount of 300.00
    
    is_valid = await validate_bill_splits(db_session, sample_bill.id)
    assert is_valid is False

@pytest.mark.asyncio
async def test_bill_split_with_invalid_account(setup_db, db_session, sample_bill):
    # Try to create a split with non-existent account
    split = BillSplit(
        bill_id=sample_bill.id,
        account_id=999,  # Non-existent account
        amount=Decimal("100.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(split)
    with pytest.raises(IntegrityError):  # Specifically expect IntegrityError
        await db_session.commit()
