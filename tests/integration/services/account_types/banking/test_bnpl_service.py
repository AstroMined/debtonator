"""
Integration tests for BNPL (Buy Now, Pay Later) account service module.

These tests verify that the specialized service functions for BNPL accounts
work correctly with the database and repository layer, validating account creation,
updates, lifecycle management, and payment scheduling.

Tests the BNPL Account service implementation for ADR-016 and ADR-019.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking import BNPLAccount
from src.services.account_types.banking import bnpl as bnpl_service


@pytest.fixture
async def bnpl_account(async_session: AsyncSession) -> BNPLAccount:
    """Create a real BNPL account for testing."""
    # Create with standard test values
    now = datetime.now(timezone.utc)
    account = BNPLAccount(
        name="Test BNPL",
        account_type="bnpl",
        available_balance=Decimal("400.00"),
        current_balance=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=now + timedelta(days=30),
        is_closed=False,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)
    return account


@pytest.fixture
async def partial_paid_bnpl_account(async_session: AsyncSession) -> BNPLAccount:
    """Create a BNPL account with some installments already paid."""
    now = datetime.now(timezone.utc)
    account = BNPLAccount(
        name="Partially Paid BNPL",
        account_type="bnpl",
        available_balance=Decimal("200.00"),
        current_balance=Decimal("200.00"),
        installment_count=4,
        installments_paid=2,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=now + timedelta(days=5),
        is_closed=False,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)
    return account


@pytest.fixture
async def past_due_bnpl_account(async_session: AsyncSession) -> BNPLAccount:
    """Create a BNPL account with payment date in the past."""
    now = datetime.now(timezone.utc)
    account = BNPLAccount(
        name="Past Due BNPL",
        account_type="bnpl",
        available_balance=Decimal("300.00"),
        current_balance=Decimal("300.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=now - timedelta(days=5),  # Payment date in the past
        is_closed=False,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)
    return account


@pytest.mark.asyncio
async def test_validate_create_valid_data(async_session: AsyncSession):
    """Test that validate_create accepts valid BNPL data."""
    # Arrange
    now = datetime.now(timezone.utc)
    data = {
        "name": "New BNPL Account",
        "account_type": "bnpl",
        "current_balance": Decimal("600.00"),
        "installment_count": 6,
        "installments_paid": 0,
        "installment_amount": Decimal("100.00"),
        "payment_frequency": "monthly",
        "next_payment_date": now + timedelta(days=30),
    }

    # Act & Assert - should not raise any exceptions
    await bnpl_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_create_missing_installment_count(async_session: AsyncSession):
    """Test that validate_create requires installment count."""
    # Arrange
    now = datetime.now(timezone.utc)
    data = {
        "name": "New BNPL Account",
        "account_type": "bnpl",
        "current_balance": Decimal("600.00"),
        "installment_amount": Decimal("100.00"),
        "payment_frequency": "monthly",
        "next_payment_date": now + timedelta(days=30),
        # Missing installment_count
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Installment count is required"):
        await bnpl_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_create_excessive_installments(async_session: AsyncSession):
    """Test that validate_create rejects excessive installment counts."""
    # Arrange
    now = datetime.now(timezone.utc)
    data = {
        "name": "New BNPL Account",
        "account_type": "bnpl",
        "current_balance": Decimal("6000.00"),
        "installment_count": 60,  # Too many installments
        "installments_paid": 0,
        "installment_amount": Decimal("100.00"),
        "payment_frequency": "monthly",
        "next_payment_date": now + timedelta(days=30),
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Installment count cannot exceed 48"):
        await bnpl_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_create_invalid_payment_frequency(async_session: AsyncSession):
    """Test that validate_create rejects invalid payment frequencies."""
    # Arrange
    now = datetime.now(timezone.utc)
    data = {
        "name": "New BNPL Account",
        "account_type": "bnpl",
        "current_balance": Decimal("600.00"),
        "installment_count": 6,
        "installments_paid": 0,
        "installment_amount": Decimal("100.00"),
        "payment_frequency": "quarterly",  # Invalid frequency
        "next_payment_date": now + timedelta(days=30),
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Payment frequency must be one of"):
        await bnpl_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_update_reduce_installment_count(
    async_session: AsyncSession, partial_paid_bnpl_account: BNPLAccount
):
    """Test that validate_update prevents reducing installment count below paid count."""
    # Arrange
    data = {"installment_count": 1}  # Can't reduce below the 2 already paid

    # Act & Assert
    with pytest.raises(
        ValueError, match="Cannot reduce installment count below already paid"
    ):
        await bnpl_service.validate_update(
            async_session, data, partial_paid_bnpl_account
        )


@pytest.mark.asyncio
async def test_validate_update_invalid_installments_paid(
    async_session: AsyncSession, bnpl_account: BNPLAccount
):
    """Test that validate_update rejects installments_paid > installment_count."""
    # Arrange
    data = {"installments_paid": 5}  # More than the total of 4

    # Act & Assert
    with pytest.raises(
        ValueError, match="Installments paid cannot exceed total installment count"
    ):
        await bnpl_service.validate_update(async_session, data, bnpl_account)


@pytest.mark.asyncio
async def test_update_overview(async_session: AsyncSession, bnpl_account: BNPLAccount):
    """Test that update_overview correctly updates the overview dict."""
    # Arrange
    overview = {
        "total_debt": Decimal("0.00"),
        "bnpl_balance": Decimal("0.00"),
    }

    # Act
    await bnpl_service.update_overview(async_session, bnpl_account, overview)

    # Assert
    assert overview["total_debt"] == Decimal("400.00")
    assert overview["bnpl_balance"] == Decimal("400.00")


@pytest.mark.asyncio
async def test_get_upcoming_payments(
    async_session: AsyncSession, bnpl_account: BNPLAccount
):
    """Test that get_upcoming_payments returns correct payment schedule."""
    # Act
    payments = await bnpl_service.get_upcoming_payments(
        async_session, bnpl_account.id, 60
    )

    # Assert
    assert len(payments) == 1
    assert payments[0]["account_id"] == bnpl_account.id
    assert payments[0]["account_name"] == "Test BNPL"
    assert payments[0]["account_type"] == "bnpl"
    assert payments[0]["amount"] == Decimal("100.00")
    assert payments[0]["remaining_installments"] == 4


@pytest.mark.asyncio
async def test_update_bnpl_status_no_change(
    async_session: AsyncSession, bnpl_account: BNPLAccount
):
    """Test that update_bnpl_status doesn't change accounts with future payment dates."""
    # Act
    updated_account = await bnpl_service.update_bnpl_status(
        async_session, bnpl_account.id
    )

    # Assert
    assert updated_account.installments_paid == 0
    assert updated_account.is_closed is False


@pytest.mark.asyncio
async def test_update_bnpl_status_increment_payment(
    async_session: AsyncSession, past_due_bnpl_account: BNPLAccount
):
    """Test that update_bnpl_status increments installments paid."""
    # Record original values to compare against
    original_payment_date = past_due_bnpl_account.next_payment_date

    # Act
    updated_account = await bnpl_service.update_bnpl_status(
        async_session, past_due_bnpl_account.id
    )

    # Assert
    assert updated_account.installments_paid == 2  # Incremented from 1
    assert updated_account.is_closed is False
    assert updated_account.current_balance == Decimal("200.00")  # Reduced by payment
    assert (
        updated_account.next_payment_date > original_payment_date
    )  # New date in future


@pytest.mark.asyncio
async def test_update_bnpl_status_final_payment(async_session: AsyncSession):
    """Test that update_bnpl_status closes account on final payment."""
    # Arrange - create account with only one payment remaining
    now = datetime.now(timezone.utc)
    account = BNPLAccount(
        name="Final Payment BNPL",
        account_type="bnpl",
        available_balance=Decimal("100.00"),
        current_balance=Decimal("100.00"),
        installment_count=4,
        installments_paid=3,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=now - timedelta(days=1),  # Payment date in the past
        is_closed=False,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)

    # Act
    updated_account = await bnpl_service.update_bnpl_status(async_session, account.id)

    # Assert
    assert updated_account.installments_paid == 4  # All paid
    assert updated_account.is_closed is True
    assert updated_account.current_balance == Decimal("0.00")


@pytest.mark.asyncio
async def test_prepare_account_data(async_session: AsyncSession):
    """Test that prepare_account_data sets defaults appropriately."""
    # Arrange
    data = {
        "name": "New BNPL Account",
        "account_type": "bnpl",
        "installment_count": 6,
        "installment_amount": Decimal("100.00"),
        # Missing optional fields
    }

    # Act
    await bnpl_service.prepare_account_data(async_session, data)

    # Assert - check defaults were set
    assert data["payment_frequency"] == "monthly"
    assert data["installments_paid"] == 0
    assert data["current_balance"] == Decimal("600.00")  # 6 × $100
    assert "next_payment_date" in data
