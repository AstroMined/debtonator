from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.schemas.liabilities import (
    AutoPaySettings,
    AutoPayUpdate,
    LiabilityCreate,
    LiabilityUpdate,
)
from src.services.liabilities import LiabilityService


@pytest.mark.asyncio
async def test_get_liabilities(db_session, test_liability):
    """Test retrieving all liabilities"""
    service = LiabilityService(db_session)
    liabilities = await service.get_liabilities()
    assert len(liabilities) == 1
    assert liabilities[0].id == test_liability.id
    assert liabilities[0].name == test_liability.name
    assert liabilities[0].amount == test_liability.amount


@pytest.mark.asyncio
async def test_get_liability(db_session, test_liability):
    """Test retrieving a specific liability"""
    service = LiabilityService(db_session)
    liability = await service.get_liability(test_liability.id)
    assert liability is not None
    assert liability.id == test_liability.id
    assert liability.name == test_liability.name
    assert liability.amount == test_liability.amount


@pytest.mark.asyncio
async def test_get_nonexistent_liability(db_session):
    """Test retrieving a non-existent liability"""
    service = LiabilityService(db_session)
    liability = await service.get_liability(999999)
    assert liability is None


@pytest.mark.asyncio
async def test_get_liabilities_by_date_range(db_session, test_liability):
    """Test retrieving liabilities within a date range"""
    service = LiabilityService(db_session)
    start_date = test_liability.due_date - timedelta(days=30)
    end_date = test_liability.due_date + timedelta(days=30)

    liabilities = await service.get_liabilities_by_date_range(start_date, end_date)
    assert len(liabilities) == 1
    assert liabilities[0].id == test_liability.id

    # Test empty range
    future_start = test_liability.due_date + timedelta(days=60)
    future_end = test_liability.due_date + timedelta(days=90)
    empty_liabilities = await service.get_liabilities_by_date_range(
        future_start, future_end
    )
    assert len(empty_liabilities) == 0


@pytest.mark.asyncio
async def test_get_unpaid_liabilities(db_session, test_liability):
    """Test retrieving unpaid liabilities"""
    service = LiabilityService(db_session)
    unpaid = await service.get_unpaid_liabilities()
    assert len(unpaid) == 1
    assert unpaid[0].id == test_liability.id


@pytest.mark.asyncio
async def test_get_unpaid_liabilities_with_payment(
    db_session, test_liability, test_payment
):
    """Test retrieving unpaid liabilities when bill has payment"""
    service = LiabilityService(db_session)
    unpaid = await service.get_unpaid_liabilities()
    assert len(unpaid) == 0


@pytest.mark.asyncio
async def test_create_liability(db_session, test_checking_account, test_category):
    """Test creating a new liability"""
    service = LiabilityService(db_session)
    liability_data = LiabilityCreate(
        name="Test Liability",
        amount=Decimal("150.00"),
        due_date=date(2025, 3, 15),
        description="Test description",
        category_id=test_category.id,
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 15},
        primary_account_id=test_checking_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
    )

    liability = await service.create_liability(liability_data)
    assert liability.name == liability_data.name
    assert liability.amount == liability_data.amount
    assert liability.due_date == liability_data.due_date
    assert liability.description == liability_data.description
    assert liability.category_id == liability_data.category_id
    assert liability.recurring == liability_data.recurring
    assert liability.recurrence_pattern == liability_data.recurrence_pattern


@pytest.mark.asyncio
async def test_update_liability(db_session, test_liability):
    """Test updating an existing liability"""
    service = LiabilityService(db_session)
    update_data = LiabilityUpdate(
        name="Updated Test Bill",
        amount=Decimal("200.00"),
        description="Updated description",
    )

    updated = await service.update_liability(test_liability.id, update_data)
    assert updated is not None
    assert updated.name == update_data.name
    assert updated.amount == update_data.amount
    assert updated.description == update_data.description
    # Unchanged fields should remain the same
    assert updated.due_date == test_liability.due_date
    assert updated.category_id == test_liability.category_id


@pytest.mark.asyncio
async def test_update_nonexistent_liability(db_session):
    """Test updating a non-existent liability"""
    service = LiabilityService(db_session)
    update_data = LiabilityUpdate(name="Updated Name")
    updated = await service.update_liability(999999, update_data)
    assert updated is None


@pytest.mark.asyncio
async def test_delete_liability(db_session, test_liability):
    """Test deleting a liability"""
    service = LiabilityService(db_session)
    result = await service.delete_liability(test_liability.id)
    assert result is True

    # Verify deletion
    liability = await service.get_liability(test_liability.id)
    assert liability is None


@pytest.mark.asyncio
async def test_delete_nonexistent_liability(db_session):
    """Test deleting a non-existent liability"""
    service = LiabilityService(db_session)
    result = await service.delete_liability(999999)
    assert result is False


@pytest.mark.asyncio
async def test_is_paid_with_payment(db_session, test_liability, test_payment):
    """Test checking if liability is paid when it has a payment"""
    service = LiabilityService(db_session)
    is_paid = await service.is_paid(test_liability.id)
    assert is_paid is True


@pytest.mark.asyncio
async def test_is_paid_without_payment(db_session, test_liability):
    """Test checking if liability is paid when it has no payments"""
    service = LiabilityService(db_session)
    is_paid = await service.is_paid(test_liability.id)
    assert is_paid is False


@pytest.mark.asyncio
async def test_update_auto_pay(db_session, test_liability):
    """Test updating auto-pay settings"""
    service = LiabilityService(db_session)

    settings = AutoPaySettings(
        preferred_pay_date=15,
        days_before_due=5,
        payment_method="bank_transfer",
        minimum_balance_required=Decimal("100.00"),
        retry_on_failure=True,
        notification_email="test@example.com",
    )

    update = AutoPayUpdate(enabled=True, settings=settings)
    updated = await service.update_auto_pay(test_liability.id, update)

    assert updated is not None
    assert updated.auto_pay is True
    assert updated.auto_pay_enabled is True
    settings_dict = settings.model_dump()
    settings_dict["minimum_balance_required"] = str(
        settings_dict["minimum_balance_required"]
    )
    assert updated.auto_pay_settings == settings_dict


@pytest.mark.asyncio
async def test_get_auto_pay_candidates(db_session, test_liability):
    """Test getting auto-pay candidates"""
    service = LiabilityService(db_session)

    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await service.update_auto_pay(test_liability.id, update)

    # Get candidates - use 30 days to ensure we catch the test bill's due date
    candidates = await service.get_auto_pay_candidates(days_ahead=30)
    assert len(candidates) == 1
    assert candidates[0].id == test_liability.id


@pytest.mark.asyncio
async def test_process_auto_pay(db_session, test_liability):
    """Test processing auto-pay"""
    service = LiabilityService(db_session)

    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await service.update_auto_pay(test_liability.id, update)

    # Process auto-pay
    result = await service.process_auto_pay(test_liability.id)
    assert result is True

    # Verify last attempt was updated
    liability = await service.get_liability(test_liability.id)
    assert liability.last_auto_pay_attempt is not None


@pytest.mark.asyncio
async def test_disable_auto_pay(db_session, test_liability):
    """Test disabling auto-pay"""
    service = LiabilityService(db_session)

    # First enable auto-pay
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await service.update_auto_pay(test_liability.id, update)

    # Then disable it
    disabled = await service.disable_auto_pay(test_liability.id)
    assert disabled is not None
    assert disabled.auto_pay_enabled is False


@pytest.mark.asyncio
async def test_get_auto_pay_status(db_session, test_liability):
    """Test getting auto-pay status"""
    service = LiabilityService(db_session)

    # First enable auto-pay with settings
    settings = AutoPaySettings(preferred_pay_date=15, payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    await service.update_auto_pay(test_liability.id, update)

    # Get status
    status = await service.get_auto_pay_status(test_liability.id)
    assert status is not None
    assert status["auto_pay"] is True
    assert status["enabled"] is True
    assert status["settings"]["preferred_pay_date"] == 15
    assert status["settings"]["payment_method"] == "bank_transfer"
    assert status["last_attempt"] is None


@pytest.mark.asyncio
async def test_auto_pay_with_nonexistent_liability(db_session):
    """Test auto-pay operations with non-existent liability"""
    service = LiabilityService(db_session)

    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)

    # Test various operations
    assert await service.update_auto_pay(999999, update) is None
    assert await service.get_auto_pay_status(999999) is None
    assert await service.process_auto_pay(999999) is False
    assert await service.disable_auto_pay(999999) is None
