"""
Integration tests for checking account service module.

These tests verify that the specialized service functions for checking accounts
work correctly with the database and repository layer, validating account creation,
updates, and other operations specific to checking accounts.

Tests the Checking Account service implementation for ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking import CheckingAccount
from src.services.account_types.banking import checking as checking_service


@pytest.fixture
async def checking_account(async_session: AsyncSession) -> CheckingAccount:
    """Create a real checking account for testing."""
    account = CheckingAccount(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        routing_number="123456789",
        account_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)
    return account


@pytest.mark.asyncio
async def test_validate_create_valid_data(async_session: AsyncSession):
    """Test that validate_create accepts valid data."""
    # Arrange
    data = {
        "name": "My Checking Account",
        "account_type": "checking",
        "current_balance": Decimal("1000.00"),
        "routing_number": "123456789",
        "account_number": "123456789",
        "has_overdraft_protection": True,
        "overdraft_limit": Decimal("500.00"),
    }

    # Act & Assert - should not raise any exceptions
    await checking_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_create_invalid_routing_number(async_session: AsyncSession):
    """Test that validate_create rejects invalid routing numbers."""
    # Arrange
    data = {
        "name": "My Checking Account",
        "account_type": "checking",
        "current_balance": Decimal("1000.00"),
        "routing_number": "12345678",  # Too short
        "account_number": "123456789",
        "has_overdraft_protection": True,
        "overdraft_limit": Decimal("500.00"),
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Routing number must be a 9-digit number"):
        await checking_service.validate_create(async_session, data)

    # Non-numeric routing number
    data["routing_number"] = "12345678A"
    with pytest.raises(ValueError, match="Routing number must be a 9-digit number"):
        await checking_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_create_missing_overdraft_limit(async_session: AsyncSession):
    """Test that validate_create requires overdraft limit when protection is enabled."""
    # Arrange
    data = {
        "name": "My Checking Account",
        "account_type": "checking",
        "current_balance": Decimal("1000.00"),
        "routing_number": "123456789",
        "account_number": "123456789",
        "has_overdraft_protection": True,  # Enabled but no limit specified
        "overdraft_limit": None,
    }

    # Act & Assert
    with pytest.raises(
        ValueError,
        match="Overdraft limit is required when overdraft protection is enabled",
    ):
        await checking_service.validate_create(async_session, data)


@pytest.mark.asyncio
async def test_validate_update_exceeds_max_overdraft(
    async_session: AsyncSession, checking_account: CheckingAccount
):
    """Test that validate_update rejects overdraft limits above maximum."""
    # Arrange
    data = {
        "overdraft_limit": Decimal("15000.00"),  # Above $10,000 limit
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Overdraft limit cannot exceed"):
        await checking_service.validate_update(async_session, data, checking_account)


@pytest.mark.asyncio
async def test_update_overview(
    async_session: AsyncSession, checking_account: CheckingAccount
):
    """Test that update_overview correctly updates the overview dict."""
    # Arrange
    overview = {
        "total_cash": Decimal("0.00"),
        "checking_balance": Decimal("0.00"),
    }

    # Act
    await checking_service.update_overview(async_session, checking_account, overview)

    # Assert
    assert overview["total_cash"] == Decimal("1000.00")
    assert overview["checking_balance"] == Decimal("1000.00")


@pytest.mark.asyncio
async def test_prepare_account_data(async_session: AsyncSession):
    """Test that prepare_account_data sets default values appropriately."""
    # Arrange
    data = {
        "name": "My Checking Account",
        "account_type": "checking",
        "has_overdraft_protection": True,
        # Overdraft limit missing but should be set by prepare_account_data
    }

    # Act
    await checking_service.prepare_account_data(async_session, data)

    # Assert
    assert "overdraft_limit" in data
    assert data["overdraft_limit"] == Decimal("500.00")


@pytest.mark.asyncio
async def test_get_upcoming_payments_empty(
    async_session: AsyncSession, checking_account: CheckingAccount
):
    """Test that get_upcoming_payments returns an empty list for checking accounts."""
    # Act
    result = await checking_service.get_upcoming_payments(
        async_session, checking_account.id, 14
    )

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_account_persistence(
    async_session: AsyncSession, checking_account: CheckingAccount
):
    """Test that account fixtures are properly persisted."""
    # Verify that the account exists in the database
    stmt = select(CheckingAccount).where(CheckingAccount.id == checking_account.id)
    result = await async_session.execute(stmt)
    db_account = result.scalar_one_or_none()

    # Assert
    assert db_account is not None
    assert db_account.name == "Test Checking"
    assert db_account.routing_number == "123456789"
    assert db_account.has_overdraft_protection is True
    assert db_account.overdraft_limit == Decimal("500.00")
