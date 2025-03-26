from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transaction_history import TransactionHistory, TransactionType
from src.utils.datetime_utils import utc_now


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
