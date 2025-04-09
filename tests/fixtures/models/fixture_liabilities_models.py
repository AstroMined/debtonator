from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability, LiabilityStatus
from src.utils.datetime_utils import days_from_now, naive_utc_now, utc_now


@pytest_asyncio.fixture
async def test_liability(
    db_session: AsyncSession,
    test_checking_account,
    test_category,
) -> Liability:
    """
    Create a test liability for use in tests.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture
        test_category: Test category fixture
        
    Returns:
        Liability: Created liability
    """
    # Create a naive datetime for DB storage (30 days from now)
    due_date = days_from_now(30).replace(tzinfo=None)

    # Create model instance directly
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=due_date,
        category_id=test_category.id,
        primary_account_id=test_checking_account.id,
        status=LiabilityStatus.PENDING,
    )

    # Add to session manually
    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)

    return liability


@pytest_asyncio.fixture
async def test_multiple_liabilities(
    db_session: AsyncSession,
    test_checking_account,
    test_category,
) -> List[Liability]:
    """
    Create multiple test liabilities with different due dates.
    
    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture
        test_category: Test category fixture
        
    Returns:
        List[Liability]: List of created liabilities with different due dates
    """
    # Setup dates for different liabilities
    now = utc_now()
    due_dates = [
        now + timedelta(days=5),  # Soon due
        now + timedelta(days=15),  # Medium term
        now + timedelta(days=30),  # Long term
        now - timedelta(days=5),  # Overdue
    ]

    liabilities = []
    for i, due_date in enumerate(due_dates):
        # Make timestamp naive for DB storage
        naive_due_date = due_date.replace(tzinfo=None)

        # Create model instance directly
        liability = Liability(
            name=f"Test Bill {i+1}",
            amount=Decimal(f"{(i+1) * 50}.00"),
            due_date=naive_due_date,
            category_id=test_category.id,
            primary_account_id=test_checking_account.id,
            paid=(i == 2),  # Make one of them paid
            recurring=(i % 2 == 0),  # Make some recurring
        )

        # Add to session manually
        db_session.add(liability)
        liabilities.append(liability)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for liability in liabilities:
        await db_session.refresh(liability)

    return liabilities


@pytest_asyncio.fixture
async def test_bill_splits(
    db_session: AsyncSession,
    test_liability,
    test_checking_account,
) -> List[BillSplit]:
    """
    Create test bill splits directly using model instantiation.
    
    Args:
        db_session: Database session fixture
        test_liability: Test liability fixture
        test_checking_account: Test checking account fixture
        
    Returns:
        List[BillSplit]: List of created bill splits
    """
    # Create multiple bill splits
    split_configs = [
        {"amount": Decimal("100.00")},
        {"amount": Decimal("100.00")},
        {"amount": Decimal("100.00")},
    ]

    splits = []
    for config in split_configs:
        # Create model instance directly
        bill_split = BillSplit(
            liability_id=test_liability.id,
            account_id=test_checking_account.id,
            amount=config["amount"],
        )

        # Add to session manually
        db_session.add(bill_split)
        splits.append(bill_split)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for split in splits:
        await db_session.refresh(split)

    return splits
