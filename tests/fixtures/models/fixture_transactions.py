from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transaction_history import TransactionHistory, TransactionType
from src.utils.datetime_utils import (
    utc_now, days_ago, start_of_day, end_of_day
)


@pytest_asyncio.fixture
async def test_transaction_history(
    db_session: AsyncSession,
    test_checking_account,
) -> TransactionHistory:
    """Create a test transaction for use in tests."""
    # Create a naive datetime for DB storage
    transaction_date = utc_now().replace(tzinfo=None)
    
    # Create model instance directly
    transaction = TransactionHistory(
        account_id=test_checking_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        description="Initial deposit",
        transaction_date=transaction_date,
    )
    
    # Add to session manually
    db_session.add(transaction)
    await db_session.flush()
    await db_session.refresh(transaction)
    
    return transaction


@pytest_asyncio.fixture
async def test_multiple_transactions(
    db_session: AsyncSession,
    test_checking_account,
    test_credit_account,
) -> List[TransactionHistory]:
    """Create multiple test transactions for use in tests."""
    now = utc_now()

    # Transaction configs for different scenarios
    transaction_configs = [
        # Recent debit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("45.67"),
            "description": "Grocery store purchase",
            "transaction_date": now - timedelta(days=2),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("954.33"),
            "category": "Groceries",
        },
        # Credit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("1200.00"),
            "description": "Salary deposit",
            "transaction_date": now - timedelta(days=7),
            "transaction_type": TransactionType.CREDIT,
            "balance_after": Decimal("2154.33"),
            "category": "Income",
        },
        # Old debit transaction on checking account
        {
            "account_id": test_checking_account.id,
            "amount": Decimal("85.23"),
            "description": "Utilities payment",
            "transaction_date": now - timedelta(days=14),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("869.10"),
            "category": "Utilities",
        },
        # Credit card payment transaction
        {
            "account_id": test_credit_account.id,
            "amount": Decimal("250.00"),
            "description": "Online purchase",
            "transaction_date": now - timedelta(days=3),
            "transaction_type": TransactionType.DEBIT,
            "balance_after": Decimal("-750.00"),
            "category": "Shopping",
        },
    ]

    transactions = []
    for config in transaction_configs:
        # Make datetime naive for DB storage
        naive_date = config["transaction_date"].replace(tzinfo=None)
        
        # Create model instance directly
        transaction = TransactionHistory(
            account_id=config["account_id"],
            amount=config["amount"],
            description=config["description"],
            transaction_date=naive_date,
            transaction_type=config["transaction_type"],
            # Removed balance_after and category as they don't exist in the model
        )
        
        # Add to session manually
        db_session.add(transaction)
        transactions.append(transaction)
    
    # Flush to get IDs and establish database rows
    await db_session.flush()
    
    # Refresh all entries to make sure they reflect what's in the database
    for transaction in transactions:
        await db_session.refresh(transaction)
        
    return transactions


@pytest_asyncio.fixture
async def test_recurring_transaction_patterns(
    db_session: AsyncSession,
    test_checking_account,
) -> List[TransactionHistory]:
    """
    Create recurring transaction patterns for pattern detection testing.
    
    Creates:
    - 4 weekly grocery transactions (Weekly Grocery Shopping)
    - 2 monthly bill payments (Monthly Internet Bill)
    
    All created directly as models, bypassing repository methods.
    """
    transactions = []
    
    # Weekly grocery transactions
    for week in range(1, 5):
        transaction_date = days_ago(week * 7).replace(tzinfo=None)  # Make naive for DB
        transaction = TransactionHistory(
            account_id=test_checking_account.id,
            amount=Decimal("75.00"),
            transaction_type=TransactionType.DEBIT,
            description="Weekly Grocery Shopping",
            transaction_date=transaction_date,
        )
        db_session.add(transaction)
        transactions.append(transaction)
        
    # Monthly bill payments
    for month in range(1, 3):
        transaction_date = days_ago(month * 30).replace(tzinfo=None)  # Make naive for DB
        transaction = TransactionHistory(
            account_id=test_checking_account.id,
            amount=Decimal("120.00"), 
            transaction_type=TransactionType.DEBIT,
            description="Monthly Internet Bill",
            transaction_date=transaction_date,
        )
        db_session.add(transaction)
        transactions.append(transaction)
        
    await db_session.flush()
    
    # Refresh all transactions to ensure they have IDs
    for transaction in transactions:
        await db_session.refresh(transaction)
        
    return transactions


@pytest_asyncio.fixture
async def test_date_range_transactions(
    db_session: AsyncSession,
    test_checking_account,
) -> List[TransactionHistory]:
    """
    Create transactions across specific date ranges for date range testing.
    
    Creates transactions at:
    - 5, 10, 15, 20, 25 days ago (inside common test ranges)
    - 30, 45, 60 days ago (outside common test ranges)
    
    Alternates between CREDIT and DEBIT types for variety.
    """
    transactions = []
    
    # Create transactions at specific intervals back from now
    date_offsets = [5, 10, 15, 20, 25, 30, 45, 60]
    
    for offset in date_offsets:
        transaction_date = days_ago(offset).replace(tzinfo=None)  # Make naive for DB
        transaction = TransactionHistory(
            account_id=test_checking_account.id,
            amount=Decimal("50.00"),
            transaction_type=TransactionType.DEBIT if offset % 2 == 0 else TransactionType.CREDIT,
            description=f"Transaction {offset} days ago",
            transaction_date=transaction_date,
        )
        db_session.add(transaction)
        transactions.append(transaction)
    
    await db_session.flush()
    
    # Refresh all transactions
    for transaction in transactions:
        await db_session.refresh(transaction)
        
    return transactions
