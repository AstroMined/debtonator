import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, text

from src.models.liabilities import Liability
from src.models.accounts import Account
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from src.schemas.bill_splits import BillSplitCreate
from src.services.liabilities import LiabilityService
from tests.conftest import TestingSessionLocal, engine


@pytest.fixture
async def liability_service(db_session):
    yield LiabilityService(db_session)

@pytest.fixture
async def test_accounts(db_session):
    # Create test accounts
    accounts = [
        Account(name="Checking", type="checking", available_balance=Decimal("1000.00")),
        Account(name="Credit", type="credit", available_balance=Decimal("0.00"), 
               total_limit=Decimal("5000.00")),
        Account(name="Savings", type="savings", available_balance=Decimal("2000.00"))
    ]
    for account in accounts:
        db_session.add(account)
    await db_session.commit()
    
    # Refresh to get IDs
    for account in accounts:
        await db_session.refresh(account)
    
    yield accounts

@pytest.mark.asyncio
async def test_create_liability_without_splits(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    liability_data = LiabilityCreate(
        name="Internet",
        amount=Decimal("89.99"),
        due_date=date(2025, 2, 15),
        description="Monthly internet bill",
        category="utilities",
        recurring=True,
        primary_account_id=checking_account.id,
        auto_pay=True,
        splits=[]
    )

    # Act
    created_liability = await liability_service.create_liability(liability_data)

    # Assert
    assert created_liability.name == "Internet"
    assert created_liability.amount == Decimal("89.99")
    assert created_liability.primary_account_id == checking_account.id
    assert created_liability.auto_pay is True
    assert created_liability.paid is False
    assert len(created_liability.splits) == 0  # No splits initially

@pytest.mark.asyncio
async def test_create_liability_with_splits(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    liability_data = LiabilityCreate(
        name="Utilities",
        amount=Decimal("150.00"),
        due_date=date(2025, 2, 15),
        description="Monthly utilities",
        category="utilities",
        recurring=True,
        primary_account_id=checking_account.id,
        auto_pay=False,
        splits=[
            BillSplitCreate(
                liability_id=None,  # Will be set after creation
                account_id=credit_account.id,
                amount=Decimal("50.00")
            )
        ]
    )

    # Act
    created_liability = await liability_service.create_liability(liability_data)

    # Assert
    assert created_liability.name == "Utilities"
    assert created_liability.amount == Decimal("150.00")
    assert len(created_liability.splits) == 1  # One split
    assert created_liability.splits[0].amount == Decimal("50.00")
    assert created_liability.splits[0].account_id == credit_account.id

@pytest.mark.asyncio
async def test_update_liability_mark_paid(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    liability_data = LiabilityCreate(
        name="Phone",
        amount=Decimal("75.00"),
        due_date=date(2025, 2, 15),
        description="Monthly phone bill",
        category="utilities",
        recurring=True,
        primary_account_id=checking_account.id,
        auto_pay=False,
        splits=[]
    )
    created_liability = await liability_service.create_liability(liability_data)
    
    # Act
    updated_liability = await liability_service.update_liability(
        created_liability.id,
        LiabilityUpdate(paid=True)
    )

    # Assert
    assert updated_liability.paid is True

@pytest.mark.asyncio
async def test_update_liability_with_new_splits(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    
    # Create initial liability without splits
    liability_data = LiabilityCreate(
        name="Rent",
        amount=Decimal("1000.00"),
        due_date=date(2025, 2, 15),
        description="Monthly rent",
        category="housing",
        recurring=True,
        primary_account_id=checking_account.id,
        auto_pay=False,
        splits=[]
    )
    created_liability = await liability_service.create_liability(liability_data)
    
    # Update with splits
    update_data = LiabilityUpdate(
        splits=[
            BillSplitCreate(
                liability_id=created_liability.id,
                account_id=credit_account.id,
                amount=Decimal("400.00")
            )
        ]
    )
    
    # Act
    updated_liability = await liability_service.update_liability(created_liability.id, update_data)

    # Assert
    assert len(updated_liability.splits) == 1  # New split
    assert updated_liability.splits[0].amount == Decimal("400.00")
    assert updated_liability.splits[0].account_id == credit_account.id

@pytest.mark.asyncio
async def test_delete_liability_cascade_splits(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    credit_account = test_accounts[1]
    
    # Create liability with splits
    liability_data = LiabilityCreate(
        name="Insurance",
        amount=Decimal("200.00"),
        due_date=date(2025, 2, 15),
        description="Car insurance",
        category="insurance",
        recurring=True,
        primary_account_id=checking_account.id,
        auto_pay=False,
        splits=[
            BillSplitCreate(
                liability_id=None,  # Will be set after creation
                account_id=credit_account.id,
                amount=Decimal("80.00")
            )
        ]
    )
    created_liability = await liability_service.create_liability(liability_data)
    
    # Act
    deleted = await liability_service.delete_liability(created_liability.id)
    
    # Assert
    assert deleted is True
    
    # Verify liability and splits are gone
    liability_result = await liability_service.get_liability(created_liability.id)
    assert liability_result is None

@pytest.mark.asyncio
async def test_get_liabilities_by_date_range(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    
    # Create liabilities with different dates
    liabilities_data = [
        LiabilityCreate(
            name="Bill 1",
            amount=Decimal("100.00"),
            due_date=date(2025, 2, 15),
            description="First bill",
            category="utilities",
            recurring=True,
            primary_account_id=checking_account.id,
            auto_pay=False,
            splits=[]
        ),
        LiabilityCreate(
            name="Bill 2",
            amount=Decimal("200.00"),
            due_date=date(2025, 3, 1),
            description="Second bill",
            category="utilities",
            recurring=True,
            primary_account_id=checking_account.id,
            auto_pay=False,
            splits=[]
        )
    ]
    
    for liability_data in liabilities_data:
        await liability_service.create_liability(liability_data)
    
    # Act
    start_date = date(2025, 2, 1)
    end_date = date(2025, 2, 28)
    liabilities = await liability_service.get_liabilities_by_date_range(start_date, end_date)
    
    # Assert
    assert len(liabilities) == 1
    assert liabilities[0].name == "Bill 1"

@pytest.mark.asyncio
async def test_get_unpaid_liabilities(liability_service, test_accounts):
    # Arrange
    checking_account = test_accounts[0]
    
    # Create paid and unpaid liabilities
    liabilities_data = [
        LiabilityCreate(
            name="Paid Bill",
            amount=Decimal("100.00"),
            due_date=date(2025, 2, 15),
            description="Paid bill",
            category="utilities",
            recurring=True,
            primary_account_id=checking_account.id,
            auto_pay=False,
            splits=[]
        ),
        LiabilityCreate(
            name="Unpaid Bill",
            amount=Decimal("200.00"),
            due_date=date(2025, 2, 20),
            description="Unpaid bill",
            category="utilities",
            recurring=True,
            primary_account_id=checking_account.id,
            auto_pay=False,
            splits=[]
        )
    ]
    
    created_liabilities = []
    for liability_data in liabilities_data:
        liability = await liability_service.create_liability(liability_data)
        created_liabilities.append(liability)
    
    # Mark first liability as paid
    await liability_service.mark_liability_paid(created_liabilities[0].id)
    
    # Act
    unpaid_liabilities = await liability_service.get_unpaid_liabilities()
    
    # Assert
    assert len(unpaid_liabilities) == 1
    assert unpaid_liabilities[0].name == "Unpaid Bill"
    assert unpaid_liabilities[0].paid is False
