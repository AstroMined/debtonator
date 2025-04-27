"""Integration tests for the cashflow historical service."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.services.cashflow.cashflow_historical_service import HistoricalService
from src.utils.datetime_utils import ensure_utc, naive_utc_from_date, utc_now, naive_utc_now


@pytest.mark.asyncio
async def test_get_historical_balance_trend(db_session: AsyncSession):
    """Test getting historical balance trend for an account."""
    # Arrange: Create account and balance history records
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create balance history records for the last 5 days
    today = utc_now().date()
    balance_history = []

    for i in range(5):
        history_date = today - timedelta(days=i)
        balance = Decimal("1000.00") + (Decimal("100.00") * i)

        history = BalanceHistory(
            account_id=account.id,
            timestamp=naive_utc_now(),
            balance=balance,
            is_reconciled=False,
        )
        balance_history.append(history)
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(session=db_session)

    # Act: Get historical balance trend
    start_date = today - timedelta(days=4)
    end_date = today
    trend = await service.get_historical_balance_trend(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify trend results
    assert len(trend) == 5  # 5 days including start and end date

    # Verify balance values in descending date order (newest first)
    assert trend[0].date == today
    assert trend[0].balance == Decimal("1000.00")  # Today's balance

    assert trend[1].date == today - timedelta(days=1)
    assert trend[1].balance == Decimal("1100.00")

    assert trend[4].date == today - timedelta(days=4)
    assert trend[4].balance == Decimal("1400.00")


@pytest.mark.asyncio
async def test_get_min_max_balance(db_session: AsyncSession):
    """Test getting minimum and maximum balance for a date range."""
    # Arrange: Create account and balance history records
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create balance history records with varying balances
    today = utc_now().date()
    balance_values = [
        Decimal("1000.00"),  # Today
        Decimal("800.00"),  # Yesterday
        Decimal("1500.00"),  # 2 days ago
        Decimal("600.00"),  # 3 days ago
        Decimal("900.00"),  # 4 days ago
    ]

    for i, balance in enumerate(balance_values):
        history_date = today - timedelta(days=i)
        history = BalanceHistory(
            account_id=account.id,
            timestamp=naive_utc_now(),
            balance=balance,
            is_reconciled=False,
        )
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(session=db_session)

    # Act: Get min and max balance in range
    start_date = today - timedelta(days=4)
    end_date = today
    min_max = await service.get_min_max_balance(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify min and max values
    assert min_max["min"] == Decimal("600.00")  # Lowest balance in range
    assert min_max["max"] == Decimal("1500.00")  # Highest balance in range
    assert min_max["start"] == Decimal("900.00")  # Balance at start date
    assert min_max["end"] == Decimal("1000.00")  # Balance at end date
    assert min_max["average"] == sum(balance_values) / len(balance_values)


@pytest.mark.asyncio
async def test_find_missing_days(db_session: AsyncSession):
    """Test finding missing days in balance history."""
    # Arrange: Create account and balance history records with gaps
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create balance history records with gaps (day 1 and day 3 missing)
    today = utc_now().date()
    recorded_days = [0, 2, 4]  # Today, 2 days ago, 4 days ago

    for i in recorded_days:
        history_date = today - timedelta(days=i)
        history = BalanceHistory(
            account_id=account.id,
            timestamp=naive_utc_now(),
            balance=Decimal("1000.00"),
            is_reconciled=False,
        )
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(session=db_session)

    # Act: Find missing days in range
    start_date = today - timedelta(days=4)
    end_date = today
    missing_days = await service.find_missing_days(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify missing days (days 1 and 3)
    assert len(missing_days) == 2
    assert (today - timedelta(days=1)) in missing_days
    assert (today - timedelta(days=3)) in missing_days


@pytest.mark.asyncio
async def test_get_historical_balance_trend_empty_range(db_session: AsyncSession):
    """Test getting historical balance trend with no records in range."""
    # Arrange: Create account but no balance history
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create historical service
    service = HistoricalService(session=db_session)

    # Act: Get historical balance trend for empty range
    today = utc_now().date()
    start_date = today - timedelta(days=10)
    end_date = today - timedelta(days=5)
    trend = await service.get_historical_balance_trend(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Empty result for range with no records
    assert len(trend) == 0


@pytest.mark.asyncio
async def test_mark_balance_reconciled(db_session: AsyncSession):
    """Test marking balance history record as reconciled."""
    # Arrange: Create account and balance history
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create balance history record
    today = utc_now().date()
    history = BalanceHistory(
        account_id=account.id,
        timestamp=naive_utc_from_date(today),
        balance=Decimal("1000.00"),
        is_reconciled=False,
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Create historical service
    service = HistoricalService(session=db_session)

    # Act: Mark balance as reconciled
    result = await service.mark_balance_reconciled(
        history_id=history.id, reconciled=True, notes="Reconciled with bank statement"
    )

    # Assert: Verify balance is marked as reconciled
    assert result is True
    assert history.reconciled is True
    assert history.notes == "Reconciled with bank statement"


@pytest.mark.asyncio
async def test_mark_balance_reconciled_not_found(db_session: AsyncSession):
    """Test marking non-existent balance history record as reconciled."""
    # Arrange: Create historical service
    service = HistoricalService(session=db_session)

    # Act & Assert: Attempt to mark non-existent record
    with pytest.raises(ValueError, match="Balance history record not found"):
        await service.mark_balance_reconciled(
            history_id=99999,  # Non-existent ID
            reconciled=True,
            notes="Reconciled with bank statement",
        )
