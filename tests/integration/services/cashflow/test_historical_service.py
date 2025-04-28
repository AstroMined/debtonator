"""
Integration tests for the cashflow historical service.

This module contains tests for the HistoricalService that follow ADR-011 datetime 
standardization requirements, using proper utility functions for all datetime operations
and reusing account fixtures for consistent test data.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance_history import BalanceHistory
from src.models.account_types.banking.checking import CheckingAccount
from src.repositories.balance_history import BalanceHistoryRepository
from src.services.cashflow.cashflow_historical_service import HistoricalService
from src.utils.datetime_utils import (
    days_ago,
    naive_days_ago,
    naive_utc_now,
    utc_now,
)


@pytest.mark.asyncio
async def test_get_historical_balance_trend(
    db_session: AsyncSession, 
    test_checking_account: CheckingAccount
):
    """
    Test getting historical balance trend for an account.
    
    Uses ADR-011 compliant datetime handling with proper naive datetime utilities
    for database records and timezone-aware datetimes for business logic.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Checking account fixture
    """
    # Create balance history records for the last 5 days with ADR-011 compliant timestamps
    balance_history = []

    for i in range(5):
        # Use naive_days_ago for database-safe timestamps
        history_date = naive_days_ago(i)
        balance = Decimal("1000.00") + (Decimal("100.00") * i)

        history = BalanceHistory(
            account_id=test_checking_account.id,
            timestamp=history_date,  # Naive UTC timestamp for DB storage
            balance=balance,
            is_reconciled=False,
        )
        balance_history.append(history)
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(db=db_session)

    # Act: Get historical balance trend using proper date range
    # Use timezone-aware dates for service interface
    today = utc_now().date()
    # Use days_ago for service parameters following ADR-011
    start_date = days_ago(4).date()
    end_date = today
    
    trend = await service.get_historical_balance_trend(
        account_id=test_checking_account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify trend results
    assert len(trend) == 5  # 5 days including start and end date (inclusive range)

    # Verify balance values in descending date order (newest first)
    # Using date equality for clarity
    assert trend[0]["date"] == today
    assert trend[0]["balance"] == Decimal("1000.00")  # Today's balance

    # Match expected dates using days_ago for consistent testing
    expected_day1 = days_ago(1).date()
    assert trend[1]["date"] == expected_day1
    assert trend[1]["balance"] == Decimal("1100.00")

    expected_day4 = days_ago(4).date()
    assert trend[4]["date"] == expected_day4
    assert trend[4]["balance"] == Decimal("1400.00")


@pytest.mark.asyncio
async def test_get_min_max_balance(
    db_session: AsyncSession, 
    test_checking_account: CheckingAccount
):
    """
    Test getting minimum and maximum balance for a date range.
    
    Uses ADR-011 compliant datetime handling with proper utility functions
    for consistent timestamp creation.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Checking account fixture
    """
    # Create balance history records with varying balances
    balance_values = [
        Decimal("1000.00"),  # Today
        Decimal("800.00"),   # Yesterday
        Decimal("1500.00"),  # 2 days ago
        Decimal("600.00"),   # 3 days ago
        Decimal("900.00"),   # 4 days ago
    ]

    for i, balance in enumerate(balance_values):
        # Use naive_days_ago for proper historical timestamps
        history = BalanceHistory(
            account_id=test_checking_account.id,
            timestamp=naive_days_ago(i),  # ADR-011 compliant timestamp
            balance=balance,
            is_reconciled=False,
        )
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(db=db_session)

    # Act: Get min and max balance in range
    # Use timezone-aware dates for service interface
    today = utc_now().date()
    start_date = days_ago(4).date()
    end_date = today
    
    min_max = await service.get_min_max_balance(
        account_id=test_checking_account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify min and max values
    assert min_max["min"] == Decimal("600.00")  # Lowest balance in range
    assert min_max["max"] == Decimal("1500.00")  # Highest balance in range
    assert min_max["start"] == Decimal("900.00")  # Balance at start date
    assert min_max["end"] == Decimal("1000.00")  # Balance at end date
    assert min_max["average"] == sum(balance_values) / len(balance_values)


@pytest.mark.asyncio
async def test_find_missing_days(
    db_session: AsyncSession, 
    test_checking_account: CheckingAccount
):
    """
    Test finding missing days in balance history.
    
    Follows ADR-011 guidance for proper date range handling and timestamp creation.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Checking account fixture
    """
    # Create balance history records with gaps (day 1 and day 3 missing)
    recorded_days = [0, 2, 4]  # Today, 2 days ago, 4 days ago

    for i in recorded_days:
        # Use naive_days_ago to create proper historical timestamps
        history = BalanceHistory(
            account_id=test_checking_account.id,
            timestamp=naive_days_ago(i),  # ADR-011 compliant timestamp
            balance=Decimal("1000.00"),
            is_reconciled=False,
        )
        db_session.add(history)

    await db_session.commit()

    # Create historical service
    service = HistoricalService(db=db_session)

    # Act: Find missing days in range using proper date range
    today = utc_now().date()
    start_date = days_ago(4).date()
    end_date = today
    
    missing_days = await service.find_missing_days(
        account_id=test_checking_account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify missing days (days 1 and 3)
    assert len(missing_days) == 2
    
    # Create expected dates using proper utility functions
    expected_missing_days = [
        days_ago(1).date(),
        days_ago(3).date()
    ]
    
    # Verify missing days match expected days
    for missing_day in missing_days:
        assert missing_day in expected_missing_days


@pytest.mark.asyncio
async def test_get_historical_balance_trend_empty_range(
    db_session: AsyncSession, 
    test_checking_account: CheckingAccount
):
    """
    Test getting historical balance trend with no records in range.
    
    Uses ADR-011 compliant datetime handling for date range creation.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Checking account fixture
    """
    # Create historical service
    service = HistoricalService(db=db_session)

    # Act: Get historical balance trend for empty range using proper date utilities
    # Use days_ago instead of manual timedelta manipulation
    start_date = days_ago(10).date()
    end_date = days_ago(5).date()
    
    trend = await service.get_historical_balance_trend(
        account_id=test_checking_account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Empty result for range with no records
    assert len(trend) == 0


@pytest.mark.asyncio
async def test_mark_balance_reconciled(
    db_session: AsyncSession, 
    test_checking_account: CheckingAccount
):
    """
    Test marking balance history record as reconciled.
    
    Uses ADR-011 compliant datetime functions for timestamp creation.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Checking account fixture
    """
    # Create balance history record with naive timestamp for DB storage
    # Use naive_utc_now instead of naive_utc_from_date for consistency
    history = BalanceHistory(
        account_id=test_checking_account.id,
        timestamp=naive_utc_now(),  # ADR-011 compliant timestamp
        balance=Decimal("1000.00"),
        is_reconciled=False,
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Create historical service
    service = HistoricalService(db=db_session)

    # Act: Mark balance as reconciled using service method
    result = await service.mark_balance_reconciled(
        history_id=history.id, 
        reconciled=True, 
        notes="Reconciled with bank statement"
    )

    # Assert: Verify balance is marked as reconciled
    await db_session.refresh(history)
    assert result is not None
    assert history.is_reconciled is True  # Field name is is_reconciled, not reconciled
    assert history.notes == "Reconciled with bank statement"


@pytest.mark.asyncio
async def test_mark_balance_reconciled_not_found(db_session: AsyncSession):
    """
    Test marking non-existent balance history record as reconciled.
    
    Verifies proper error handling when record is not found.
    
    Args:
        db_session: Database session fixture
    """
    # Create historical service
    service = HistoricalService(db=db_session)

    # Act & Assert: Attempt to mark non-existent record
    with pytest.raises(ValueError, match="Balance history record not found"):
        await service.mark_balance_reconciled(
            history_id=99999,  # Non-existent ID
            reconciled=True,
            notes="Reconciled with bank statement",
        )
