import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, text

from src.models.bills import Bill
from src.models.accounts import Account
from src.schemas.bills import BillCreate, BillUpdate, BillSplitInput
from src.services.bills import BillService
from tests.conftest import TestingSessionLocal, engine


@pytest.fixture
async def session(setup_db):  # Depend on setup_db to ensure tables are created
    async with TestingSessionLocal() as session:
        await session.execute(text("PRAGMA foreign_keys=ON"))
        await session.commit()
        yield session

@pytest.fixture
async def bill_service(session):
    yield BillService(session)

@pytest.fixture
async def test_accounts(session):
    # Create test accounts
    accounts = [
        Account(name="Checking", type="checking", available_balance=Decimal("1000.00")),
        Account(name="Credit", type="credit", available_balance=Decimal("0.00"), 
               total_limit=Decimal("5000.00")),
        Account(name="Savings", type="savings", available_balance=Decimal("2000.00"))
    ]
    for account in accounts:
        session.add(account)
    await session.commit()
    
    # Refresh to get IDs
    for account in accounts:
        await session.refresh(account)
    
    yield accounts

@pytest.mark.asyncio
async def test_create_bill_without_splits(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Internet",
        amount=Decimal("89.99"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=True,
        splits=[]
    )

    # Act
    created_bill = await bill_service.create_bill(bill_data)

    # Assert
    assert created_bill.bill_name == "Internet"
    assert created_bill.amount == Decimal("89.99")
    assert created_bill.account_id == checking_account.id
    assert created_bill.account_name == checking_account.name
    assert created_bill.auto_pay is True
    assert created_bill.paid is False
    assert created_bill.up_to_date is True
    assert len(created_bill.splits) == 1  # Should have one split for primary account
    assert created_bill.splits[0].amount == Decimal("89.99")
    assert created_bill.splits[0].account_id == checking_account.id

@pytest.mark.asyncio
async def test_create_bill_with_splits(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Utilities",
        amount=Decimal("150.00"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=False,
        splits=[
            BillSplitInput(
                account_id=credit_account.id,
                amount=Decimal("50.00")
            )
        ]
    )

    # Act
    created_bill = await bill_service.create_bill(bill_data)

    # Assert
    assert created_bill.bill_name == "Utilities"
    assert created_bill.amount == Decimal("150.00")
    assert len(created_bill.splits) == 2  # Primary account split + additional split
    
    # Verify splits
    split_amounts = {split.account_id: split.amount for split in created_bill.splits}
    assert split_amounts[checking_account.id] == Decimal("100.00")  # Primary gets remainder
    assert split_amounts[credit_account.id] == Decimal("50.00")

@pytest.mark.asyncio
async def test_create_bill_validates_split_total(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Invalid Split",
        amount=Decimal("100.00"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=False,
        splits=[
            BillSplitInput(
                account_id=credit_account.id,
                amount=Decimal("100.00")  # Equal to total, should fail
            )
        ]
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Split amounts total .* exceeds or equals bill amount"):
        await bill_service.create_bill(bill_data)

@pytest.mark.asyncio
async def test_update_bill_mark_paid(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Phone",
        amount=Decimal("75.00"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=False,
        splits=[]
    )
    created_bill = await bill_service.create_bill(bill_data)
    
    # Act
    updated_bill = await bill_service.update_bill(
        created_bill.id,
        BillUpdate(paid=True)
    )

    # Assert
    assert updated_bill.paid is True
    assert updated_bill.paid_date == date.today()

@pytest.mark.asyncio
async def test_update_bill_with_new_splits(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    
    # Create initial bill without splits
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Rent",
        amount=Decimal("1000.00"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=False,
        splits=[]
    )
    created_bill = await bill_service.create_bill(bill_data)
    
    # Update with splits
    update_data = BillUpdate(
        splits=[
            BillSplitInput(
                account_id=credit_account.id,
                amount=Decimal("400.00")
            )
        ]
    )
    
    # Act
    updated_bill = await bill_service.update_bill(created_bill.id, update_data)

    # Assert
    assert len(updated_bill.splits) == 2  # Primary + new split
    split_amounts = {split.account_id: split.amount for split in updated_bill.splits}
    assert split_amounts[checking_account.id] == Decimal("600.00")  # Primary gets remainder
    assert split_amounts[credit_account.id] == Decimal("400.00")

@pytest.mark.asyncio
async def test_delete_bill_cascade_splits(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    
    # Create bill with splits
    bill_data = BillCreate(
        month="02",
        day_of_month=15,
        bill_name="Insurance",
        amount=Decimal("200.00"),
        account_id=checking_account.id,
        account_name=checking_account.name,
        auto_pay=False,
        splits=[
            BillSplitInput(
                account_id=credit_account.id,
                amount=Decimal("80.00")
            )
        ]
    )
    created_bill = await bill_service.create_bill(bill_data)
    
    # Act
    deleted = await bill_service.delete_bill(created_bill.id)
    
    # Assert
    assert deleted is True
    
    # Verify bill and splits are gone
    bill_result = await bill_service.get_bill(created_bill.id)
    assert bill_result is None

@pytest.mark.asyncio
async def test_get_bills_by_date_range(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    
    # Create bills with different dates
    bills_data = [
        BillCreate(
            month="02",
            day_of_month=15,
            bill_name="Bill 1",
            amount=Decimal("100.00"),
            account_id=checking_account.id,
            account_name=checking_account.name,
            auto_pay=False,
            splits=[]
        ),
        BillCreate(
            month="03",
            day_of_month=1,
            bill_name="Bill 2",
            amount=Decimal("200.00"),
            account_id=checking_account.id,
            account_name=checking_account.name,
            auto_pay=False,
            splits=[]
        )
    ]
    
    for bill_data in bills_data:
        await bill_service.create_bill(bill_data)
    
    # Act
    start_date = date(2025, 2, 1)
    end_date = date(2025, 2, 28)
    bills = await bill_service.get_bills_by_date_range(start_date, end_date)
    
    # Assert
    assert len(bills) == 1
    assert bills[0].bill_name == "Bill 1"

@pytest.mark.asyncio
async def test_get_unpaid_bills(bill_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    
    # Create paid and unpaid bills
    bills_data = [
        BillCreate(
            month="02",
            day_of_month=15,
            bill_name="Paid Bill",
            amount=Decimal("100.00"),
            account_id=checking_account.id,
            account_name=checking_account.name,
            auto_pay=False,
            splits=[]
        ),
        BillCreate(
            month="02",
            day_of_month=20,
            bill_name="Unpaid Bill",
            amount=Decimal("200.00"),
            account_id=checking_account.id,
            account_name=checking_account.name,
            auto_pay=False,
            splits=[]
        )
    ]
    
    created_bills = []
    for bill_data in bills_data:
        bill = await bill_service.create_bill(bill_data)
        created_bills.append(bill)
    
    # Mark first bill as paid
    await bill_service.mark_bill_paid(created_bills[0].id)
    
    # Act
    unpaid_bills = await bill_service.get_unpaid_bills()
    
    # Assert
    assert len(unpaid_bills) == 1
    assert unpaid_bills[0].bill_name == "Unpaid Bill"
    assert unpaid_bills[0].paid is False
