from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
from src.schemas.income import IncomeCreate, IncomeFilters, IncomeUpdate
from src.services.income import IncomeService


@pytest.fixture(scope="function")
async def income_service(db_session: AsyncSession):
    return IncomeService(db_session)


@pytest.mark.asyncio
async def test_create_income(
    income_service: IncomeService,
    test_checking_account: Account,
    db_session: AsyncSession,
):
    """Test creating a new income entry"""
    # Create income data
    income_create = IncomeCreate(
        date=date(2025, 2, 20),
        source="Test Source",
        amount=Decimal("1000.00"),
        deposited=False,
        account_id=test_checking_account.id,
    )

    # Create the income entry
    income = await income_service.create(income_create)

    # Verify income was created
    assert income is not None
    assert income.source == "Test Source"
    assert income.amount == Decimal("1000.00")
    assert income.deposited is False
    assert income.account_id == test_checking_account.id
    assert income.account is not None  # Verify relationship loading


@pytest.mark.asyncio
async def test_create_income_invalid_account(
    income_service: IncomeService, db_session: AsyncSession
):
    """Test creating income with non-existent account"""
    income_create = IncomeCreate(
        date=date(2025, 2, 20),
        source="Test Source",
        amount=Decimal("1000.00"),
        deposited=False,
        account_id=99999,  # Non-existent account ID
    )

    # Attempt to create income should raise HTTPException
    with pytest.raises(HTTPException, match="Account not found"):
        await income_service.create(income_create)


@pytest.mark.asyncio
async def test_get_income(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test retrieving a single income entry"""
    # Get the income entry
    income = await income_service.get(test_income.id)

    # Verify income data
    assert income is not None
    assert income.id == test_income.id
    assert income.amount == test_income.amount
    assert income.source == test_income.source
    assert income.account is not None  # Verify relationship loading


@pytest.mark.asyncio
async def test_update_income(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test updating an existing income entry"""
    # Create update data
    income_update = IncomeUpdate(source="Updated Source", amount=Decimal("1500.00"))

    # Update the income entry
    updated_income = await income_service.update(test_income.id, income_update)

    # Verify income was updated
    assert updated_income is not None
    assert updated_income.source == "Updated Source"
    assert updated_income.amount == Decimal("1500.00")
    assert updated_income.account is not None  # Verify relationship loading


@pytest.mark.asyncio
async def test_update_income_not_found(
    income_service: IncomeService, db_session: AsyncSession
):
    """Test updating a non-existent income entry"""
    income_update = IncomeUpdate(source="Updated Source")

    # Update non-existent income
    updated_income = await income_service.update(99999, income_update)
    assert updated_income is None


@pytest.mark.asyncio
async def test_update_income_deposit_status(
    income_service: IncomeService,
    test_income: Income,
    test_checking_account: Account,
    db_session: AsyncSession,
):
    """Test updating income deposit status and account balance"""
    original_balance = test_checking_account.available_balance

    # Update income to deposited
    income_update = IncomeUpdate(deposited=True)
    updated_income = await income_service.update(test_income.id, income_update)

    # Verify income was updated and account balance increased
    assert updated_income is not None
    assert updated_income.deposited is True
    assert (
        updated_income.account.available_balance
        == original_balance + test_income.amount
    )


@pytest.mark.asyncio
async def test_delete_income(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test deleting an income entry"""
    # Delete the income entry
    result = await income_service.delete(test_income.id)
    assert result is True

    # Verify income was deleted
    deleted_income = await income_service.get(test_income.id)
    assert deleted_income is None


@pytest.mark.asyncio
async def test_delete_income_not_found(
    income_service: IncomeService, db_session: AsyncSession
):
    """Test deleting a non-existent income entry"""
    result = await income_service.delete(99999)
    assert result is False


@pytest.mark.asyncio
async def test_list_income_with_filters(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test listing income entries with filters"""
    # Create filters
    filters = IncomeFilters(
        start_date=date(2025, 2, 1),
        end_date=date(2025, 2, 28),
        source="Test",
        deposited=False,
        min_amount=Decimal("50.00"),
        max_amount=Decimal("2000.00"),
    )

    # Get filtered income entries
    items, total = await income_service.list(filters)

    # Verify results
    assert total == 1
    assert len(items) == 1
    assert items[0].id == test_income.id


@pytest.mark.asyncio
async def test_get_undeposited(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test retrieving undeposited income entries"""
    # Get undeposited income
    undeposited = await income_service.get_undeposited()

    # Verify results
    assert len(undeposited) == 1
    assert undeposited[0].id == test_income.id
    assert undeposited[0].deposited is False


@pytest.mark.asyncio
async def test_mark_as_deposited(
    income_service: IncomeService,
    test_income: Income,
    test_checking_account: Account,
    db_session: AsyncSession,
):
    """Test marking income as deposited"""
    original_balance = test_checking_account.available_balance

    # Mark income as deposited
    updated_income = await income_service.mark_as_deposited(test_income.id)

    # Verify income was updated and account balance increased
    assert updated_income is not None
    assert updated_income.deposited is True
    assert (
        updated_income.account.available_balance
        == original_balance + test_income.amount
    )


@pytest.mark.asyncio
async def test_get_total_undeposited(
    income_service: IncomeService, test_income: Income, db_session: AsyncSession
):
    """Test getting total undeposited amount"""
    # Get total undeposited amount
    total = await income_service.get_total_undeposited()

    # Verify total matches test_income amount
    assert total == test_income.amount
