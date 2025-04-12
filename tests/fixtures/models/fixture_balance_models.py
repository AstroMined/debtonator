from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance_history import BalanceHistory
from src.models.balance_reconciliation import BalanceReconciliation
from src.utils.datetime_utils import days_ago, naive_utc_now, utc_now


@pytest_asyncio.fixture
async def test_balance_history(
    db_session: AsyncSession,
    test_checking_account,
) -> BalanceHistory:
    """
    Create a test balance history record for use in tests.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture

    Returns:
        BalanceHistory: Created balance history record
    """
    # Get a naive UTC timestamp for DB storage
    timestamp = naive_utc_now()

    # Create model instance directly
    balance = BalanceHistory(
        account_id=test_checking_account.id,
        balance=Decimal("1000.00"),
        is_reconciled=False,
        notes="Initial balance",
        timestamp=timestamp,
    )

    # Add to session manually
    db_session.add(balance)
    await db_session.flush()
    await db_session.refresh(balance)

    return balance


@pytest_asyncio.fixture
async def test_multiple_balances(
    db_session: AsyncSession,
    test_checking_account,
) -> List[BalanceHistory]:
    """
    Create multiple balance history records for use in tests.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture

    Returns:
        List[BalanceHistory]: List of created balance history records
    """
    now = utc_now()
    balance_configs = [
        (now - timedelta(days=20), Decimal("1000.00"), False, "Initial balance"),
        (now - timedelta(days=10), Decimal("1500.00"), True, "After paycheck deposit"),
        (now, Decimal("2000.00"), False, "Current balance"),
    ]

    balances = []
    for timestamp, amount, reconciled, note in balance_configs:
        # Make timestamp naive for DB storage
        naive_timestamp = timestamp.replace(tzinfo=None)

        # Create model instance directly
        balance = BalanceHistory(
            account_id=test_checking_account.id,
            balance=amount,
            is_reconciled=reconciled,
            notes=note,
            timestamp=naive_timestamp,
        )

        # Add to session manually
        db_session.add(balance)
        balances.append(balance)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for balance in balances:
        await db_session.refresh(balance)

    return balances


@pytest_asyncio.fixture
async def test_balance_reconciliation(
    db_session: AsyncSession,
    test_checking_account,
) -> BalanceReconciliation:
    """
    Create a test balance reconciliation entry for use in tests.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture

    Returns:
        BalanceReconciliation: Created balance reconciliation record
    """
    # Create a naive datetime for DB storage
    naive_date = naive_utc_now()

    # Create model instance directly
    reconciliation = BalanceReconciliation(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1025.50"),
        adjustment_amount=Decimal("25.50"),  # Explicitly set the calculated amount
        reason="Initial reconciliation after transaction verification",
        reconciliation_date=naive_date,
    )

    # Add to session manually
    db_session.add(reconciliation)
    await db_session.flush()
    await db_session.refresh(reconciliation)

    return reconciliation


@pytest_asyncio.fixture
async def test_multiple_reconciliations(
    db_session: AsyncSession,
    test_checking_account,
) -> List[BalanceReconciliation]:
    """
    Create multiple balance reconciliation entries for testing.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture

    Returns:
        List[BalanceReconciliation]: List of created balance reconciliation records
    """
    # Create multiple reconciliation entries with different dates
    entries = []

    for i, x_days_ago in enumerate([90, 60, 30, 15, 5]):
        # Calculate dates as naive datetimes (without timezone info)
        naive_date = days_ago(x_days_ago).replace(tzinfo=None)

        # Create model instance directly
        entry = BalanceReconciliation(
            account_id=test_checking_account.id,
            previous_balance=Decimal(f"{1000 + (i * 50)}.00"),
            new_balance=Decimal(f"{1000 + ((i + 1) * 50)}.00"),
            adjustment_amount=Decimal("50.00"),  # Explicitly set the calculated amount
            reason=f"Reconciliation #{i + 1}",
            reconciliation_date=naive_date,  # Directly use naive datetime
        )

        # Add to session manually
        db_session.add(entry)
        entries.append(entry)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for entry in entries:
        await db_session.refresh(entry)

    return entries


@pytest_asyncio.fixture
async def test_balance_history_with_gaps(
    db_session: AsyncSession,
    test_checking_account,
) -> List[BalanceHistory]:
    """
    Create balance history records with specific gaps for missing days test.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture

    Returns:
        List[BalanceHistory]: List of created balance history records with gaps
    """
    now = utc_now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Create exactly 3 balance entries with specific dates
    # This should result in exactly 8 missing days
    balance_dates = [
        today,  # Today (day 0)
        today - timedelta(days=5),  # 5 days ago
        today - timedelta(days=10),  # 10 days ago
    ]

    balances = []
    for i, timestamp in enumerate(balance_dates):
        # Create model directly (not using repository)
        balance = BalanceHistory(
            account_id=test_checking_account.id,
            balance=Decimal(f"{1000 + (i * 200)}.00"),
            is_reconciled=False,
            notes=f"Balance entry {i+1}",
            timestamp=timestamp.replace(tzinfo=None),  # Make naive for DB
        )

        db_session.add(balance)
        balances.append(balance)

    await db_session.flush()

    # Refresh to ensure database state is reflected
    for balance in balances:
        await db_session.refresh(balance)

    # Removed print statement as per code review
    return balances
