import pytest
from decimal import Decimal
from datetime import date, datetime

from src.models.bill_splits import BillSplit
from src.services.bill_splits import BillSplitService, calculate_split_totals, validate_bill_splits
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate

@pytest.fixture
async def base_bill_split(db_session, base_bill, base_account):
    """Create a basic bill split for testing"""
    split = BillSplit(
        liability_id=base_bill.id,
        account_id=base_account.id,
        amount=Decimal("50.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(split)
    await db_session.flush()
    await db_session.refresh(split)
    return split

@pytest.mark.asyncio
async def test_get_bill_splits(db_session, base_bill_split):
    """Test retrieving all splits for a liability"""
    service = BillSplitService(db_session)
    splits = await service.get_bill_splits(base_bill_split.liability_id)
    assert len(splits) == 1
    assert splits[0].id == base_bill_split.id
    assert splits[0].amount == base_bill_split.amount

@pytest.mark.asyncio
async def test_get_account_splits(db_session, base_bill_split):
    """Test retrieving all splits for an account"""
    service = BillSplitService(db_session)
    splits = await service.get_account_splits(base_bill_split.account_id)
    assert len(splits) == 1
    assert splits[0].id == base_bill_split.id
    assert splits[0].amount == base_bill_split.amount

@pytest.mark.asyncio
async def test_create_bill_split(db_session, base_bill, base_account):
    """Test creating a new bill split"""
    service = BillSplitService(db_session)
    split_data = BillSplitCreate(
        liability_id=base_bill.id,
        account_id=base_account.id,
        amount=Decimal("75.00")
    )
    split = await service.create_bill_split(split_data)
    assert split.liability_id == base_bill.id
    assert split.account_id == base_account.id
    assert split.amount == Decimal("75.00")

@pytest.mark.asyncio
async def test_create_bill_split_invalid_liability(db_session, base_account):
    """Test creating a split with invalid liability ID"""
    service = BillSplitService(db_session)
    split_data = BillSplitCreate(
        liability_id=999999,  # Non-existent ID
        account_id=base_account.id,
        amount=Decimal("75.00")
    )
    with pytest.raises(ValueError, match="Liability with id 999999 not found"):
        await service.create_bill_split(split_data)

@pytest.mark.asyncio
async def test_update_bill_split(db_session, base_bill_split):
    """Test updating an existing bill split"""
    service = BillSplitService(db_session)
    update_data = BillSplitUpdate(amount=Decimal("60.00"))
    updated_split = await service.update_bill_split(base_bill_split.id, update_data)
    assert updated_split is not None
    assert updated_split.amount == Decimal("60.00")

@pytest.mark.asyncio
async def test_update_nonexistent_bill_split(db_session):
    """Test updating a non-existent bill split"""
    service = BillSplitService(db_session)
    update_data = BillSplitUpdate(amount=Decimal("60.00"))
    updated_split = await service.update_bill_split(999999, update_data)
    assert updated_split is None

@pytest.mark.asyncio
async def test_delete_bill_split(db_session, base_bill_split):
    """Test deleting a specific bill split"""
    service = BillSplitService(db_session)
    result = await service.delete_bill_split(base_bill_split.id)
    assert result is True
    
    # Verify split was deleted
    splits = await service.get_bill_splits(base_bill_split.liability_id)
    assert len(splits) == 0

@pytest.mark.asyncio
async def test_delete_nonexistent_bill_split(db_session):
    """Test deleting a non-existent bill split"""
    service = BillSplitService(db_session)
    result = await service.delete_bill_split(999999)
    assert result is False

@pytest.mark.asyncio
async def test_delete_bill_splits(db_session, base_bill_split):
    """Test deleting all splits for a liability"""
    service = BillSplitService(db_session)
    await service.delete_bill_splits(base_bill_split.liability_id)
    
    # Verify splits were deleted
    splits = await service.get_bill_splits(base_bill_split.liability_id)
    assert len(splits) == 0

@pytest.mark.asyncio
async def test_calculate_split_totals(db_session, base_bill, base_account):
    """Test calculating total amount of splits"""
    # Create multiple splits
    splits = [
        BillSplit(
            liability_id=base_bill.id,
            account_id=base_account.id,
            amount=Decimal("50.00"),
            created_at=date.today(),
            updated_at=date.today()
        ),
        BillSplit(
            liability_id=base_bill.id,
            account_id=base_account.id,
            amount=Decimal("50.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    for split in splits:
        db_session.add(split)
    await db_session.flush()
    
    total = await calculate_split_totals(db_session, base_bill.id)
    assert total == Decimal("100.00")

@pytest.mark.asyncio
async def test_validate_bill_splits_valid(db_session, base_bill, base_account):
    """Test validating splits match liability amount"""
    # Create splits that sum to liability amount
    splits = [
        BillSplit(
            liability_id=base_bill.id,
            account_id=base_account.id,
            amount=Decimal("50.00"),
            created_at=date.today(),
            updated_at=date.today()
        ),
        BillSplit(
            liability_id=base_bill.id,
            account_id=base_account.id,
            amount=Decimal("50.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    for split in splits:
        db_session.add(split)
    await db_session.flush()
    
    is_valid = await validate_bill_splits(db_session, base_bill.id)
    assert is_valid is True

@pytest.mark.asyncio
async def test_validate_bill_splits_invalid(db_session, base_bill, base_account):
    """Test validating splits don't match liability amount"""
    # Create split that doesn't sum to liability amount
    split = BillSplit(
        liability_id=base_bill.id,
        account_id=base_account.id,
        amount=Decimal("50.00"),  # Less than liability amount of 100.00
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(split)
    await db_session.flush()
    
    is_valid = await validate_bill_splits(db_session, base_bill.id)
    assert is_valid is False
