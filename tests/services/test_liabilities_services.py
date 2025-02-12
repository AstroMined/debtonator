import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.services.liabilities import LiabilityService
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate

@pytest.mark.asyncio
async def test_get_liabilities(db_session, base_bill):
    """Test retrieving all liabilities"""
    service = LiabilityService(db_session)
    liabilities = await service.get_liabilities()
    assert len(liabilities) == 1
    assert liabilities[0].id == base_bill.id
    assert liabilities[0].name == base_bill.name
    assert liabilities[0].amount == base_bill.amount

@pytest.mark.asyncio
async def test_get_liability(db_session, base_bill):
    """Test retrieving a specific liability"""
    service = LiabilityService(db_session)
    liability = await service.get_liability(base_bill.id)
    assert liability is not None
    assert liability.id == base_bill.id
    assert liability.name == base_bill.name
    assert liability.amount == base_bill.amount

@pytest.mark.asyncio
async def test_get_nonexistent_liability(db_session):
    """Test retrieving a non-existent liability"""
    service = LiabilityService(db_session)
    liability = await service.get_liability(999999)
    assert liability is None

@pytest.mark.asyncio
async def test_get_liabilities_by_date_range(db_session, base_bill):
    """Test retrieving liabilities within a date range"""
    service = LiabilityService(db_session)
    start_date = base_bill.due_date - timedelta(days=30)
    end_date = base_bill.due_date + timedelta(days=30)
    
    liabilities = await service.get_liabilities_by_date_range(start_date, end_date)
    assert len(liabilities) == 1
    assert liabilities[0].id == base_bill.id

    # Test empty range
    future_start = base_bill.due_date + timedelta(days=60)
    future_end = base_bill.due_date + timedelta(days=90)
    empty_liabilities = await service.get_liabilities_by_date_range(future_start, future_end)
    assert len(empty_liabilities) == 0

@pytest.mark.asyncio
async def test_get_unpaid_liabilities(db_session, base_bill):
    """Test retrieving unpaid liabilities"""
    service = LiabilityService(db_session)
    unpaid = await service.get_unpaid_liabilities()
    assert len(unpaid) == 1
    assert unpaid[0].id == base_bill.id

@pytest.mark.asyncio
async def test_get_unpaid_liabilities_with_payment(db_session, base_bill, base_payment):
    """Test retrieving unpaid liabilities when bill has payment"""
    service = LiabilityService(db_session)
    unpaid = await service.get_unpaid_liabilities()
    assert len(unpaid) == 0

@pytest.mark.asyncio
async def test_create_liability(db_session, base_account):
    """Test creating a new liability"""
    service = LiabilityService(db_session)
    liability_data = LiabilityCreate(
        name="Test Liability",
        amount=Decimal("150.00"),
        due_date=date(2025, 3, 15),
        description="Test description",
        category="Test",
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 15},
        primary_account_id=base_account.id
    )
    
    liability = await service.create_liability(liability_data)
    assert liability.name == liability_data.name
    assert liability.amount == liability_data.amount
    assert liability.due_date == liability_data.due_date
    assert liability.description == liability_data.description
    assert liability.category == liability_data.category
    assert liability.recurring == liability_data.recurring
    assert liability.recurrence_pattern == liability_data.recurrence_pattern

@pytest.mark.asyncio
async def test_update_liability(db_session, base_bill):
    """Test updating an existing liability"""
    service = LiabilityService(db_session)
    update_data = LiabilityUpdate(
        name="Updated Test Bill",
        amount=Decimal("200.00"),
        description="Updated description"
    )
    
    updated = await service.update_liability(base_bill.id, update_data)
    assert updated is not None
    assert updated.name == update_data.name
    assert updated.amount == update_data.amount
    assert updated.description == update_data.description
    # Unchanged fields should remain the same
    assert updated.due_date == base_bill.due_date
    assert updated.category == base_bill.category

@pytest.mark.asyncio
async def test_update_nonexistent_liability(db_session):
    """Test updating a non-existent liability"""
    service = LiabilityService(db_session)
    update_data = LiabilityUpdate(name="Updated Name")
    updated = await service.update_liability(999999, update_data)
    assert updated is None

@pytest.mark.asyncio
async def test_delete_liability(db_session, base_bill):
    """Test deleting a liability"""
    service = LiabilityService(db_session)
    result = await service.delete_liability(base_bill.id)
    assert result is True
    
    # Verify deletion
    liability = await service.get_liability(base_bill.id)
    assert liability is None

@pytest.mark.asyncio
async def test_delete_nonexistent_liability(db_session):
    """Test deleting a non-existent liability"""
    service = LiabilityService(db_session)
    result = await service.delete_liability(999999)
    assert result is False

@pytest.mark.asyncio
async def test_is_paid_with_payment(db_session, base_bill, base_payment):
    """Test checking if liability is paid when it has a payment"""
    service = LiabilityService(db_session)
    is_paid = await service.is_paid(base_bill.id)
    assert is_paid is True

@pytest.mark.asyncio
async def test_is_paid_without_payment(db_session, base_bill):
    """Test checking if liability is paid when it has no payments"""
    service = LiabilityService(db_session)
    is_paid = await service.is_paid(base_bill.id)
    assert is_paid is False
