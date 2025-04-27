"""Integration tests for the cashflow transaction service."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType
from src.services.cashflow.cashflow_transaction_service import TransactionService
from src.utils.datetime_utils import ensure_utc, naive_utc_from_date, utc_now, naive_utc_now


@pytest.mark.asyncio
async def test_get_recent_transactions(db_session: AsyncSession):
    """Test getting recent transactions for an account."""
    # Arrange: Create account and transactions
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create transactions for last 5 days
    today = utc_now().date()
    transactions = []

    for i in range(5):
        # Alternating deposits and withdrawals
        amount = Decimal("100.00") if i % 2 == 0 else Decimal("-50.00")
        trans_type = (
            TransactionType.DEPOSIT if i % 2 == 0 else TransactionType.WITHDRAWAL
        )

        trans_date = today - timedelta(days=i)
        transaction = TransactionHistory(
            account_id=account.id,
            transaction_date=naive_utc_now(),
            description=f"Transaction {i+1}",
            amount=amount,
            transaction_type=trans_type,
            balance_after=Decimal("1000.00") + amount,
            category="Test",
        )
        transactions.append(transaction)
        db_session.add(transaction)

    await db_session.commit()

    # Create transaction service
    service = TransactionService(session=db_session)

    # Act: Get recent transactions
    recent_trans = await service.get_recent_transactions(account_id=account.id, days=3)

    # Assert: Verify recent transactions
    assert len(recent_trans) == 3  # Last 3 days of transactions

    # Transactions should be in date order (newest first)
    assert recent_trans[0].date.date() == today
    assert recent_trans[1].date.date() == today - timedelta(days=1)
    assert recent_trans[2].date.date() == today - timedelta(days=2)


@pytest.mark.asyncio
async def test_analyze_spending_by_category(db_session: AsyncSession):
    """Test analyzing spending by category."""
    # Arrange: Create account and transactions with categories
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create transactions with different categories
    today = utc_now().date()
    categories = ["Groceries", "Utilities", "Entertainment", "Groceries"]
    amounts = [
        Decimal("-50.00"),
        Decimal("-100.00"),
        Decimal("-75.00"),
        Decimal("-25.00"),
    ]

    for i in range(4):
        trans_date = today - timedelta(days=i)
        transaction = TransactionHistory(
            account_id=account.id,
            transaction_date=naive_utc_now(),
            description=f"Transaction {i+1}",
            amount=amounts[i],
            type=TransactionType.WITHDRAWAL,
            balance_after=Decimal("1000.00") + amounts[i],
            category=categories[i],
        )
        db_session.add(transaction)

    await db_session.commit()

    # Create transaction service
    service = TransactionService(session=db_session)

    # Act: Analyze spending by category
    start_date = today - timedelta(days=4)
    end_date = today
    category_spending = await service.analyze_spending_by_category(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify spending by category
    assert len(category_spending) == 3  # 3 unique categories

    # Check individual category totals
    groceries_total = next(
        (item for item in category_spending if item["category"] == "Groceries"), None
    )
    assert groceries_total is not None
    assert groceries_total["total"] == Decimal("75.00")  # 50 + 25

    utilities_total = next(
        (item for item in category_spending if item["category"] == "Utilities"), None
    )
    assert utilities_total is not None
    assert utilities_total["total"] == Decimal("100.00")

    entertainment_total = next(
        (item for item in category_spending if item["category"] == "Entertainment"),
        None,
    )
    assert entertainment_total is not None
    assert entertainment_total["total"] == Decimal("75.00")


@pytest.mark.asyncio
async def test_get_cash_flow_summary(db_session: AsyncSession):
    """Test getting cash flow summary for a date range."""
    # Arrange: Create account and transactions
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create mix of deposits and withdrawals
    today = utc_now().date()
    transaction_data = [
        {"amount": Decimal("500.00"), "type": TransactionType.DEPOSIT},
        {"amount": Decimal("-200.00"), "type": TransactionType.WITHDRAWAL},
        {"amount": Decimal("300.00"), "type": TransactionType.DEPOSIT},
        {"amount": Decimal("-150.00"), "type": TransactionType.WITHDRAWAL},
    ]

    for i, data in enumerate(transaction_data):
        trans_date = today - timedelta(days=i)
        transaction = TransactionHistory(
            account_id=account.id,
            transaction_date=naive_utc_now(),
            description=f"Transaction {i+1}",
            amount=data["amount"],
            type=data["type"],
            balance_after=Decimal("1000.00") + data["amount"],
            category="Test",
        )
        db_session.add(transaction)

    await db_session.commit()

    # Create transaction service
    service = TransactionService(session=db_session)

    # Act: Get cash flow summary
    start_date = today - timedelta(days=4)
    end_date = today
    summary = await service.get_cash_flow_summary(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify cash flow summary
    assert summary["total_inflow"] == Decimal("800.00")  # 500 + 300
    assert summary["total_outflow"] == Decimal("350.00")  # 200 + 150
    assert summary["net_flow"] == Decimal("450.00")  # 800 - 350


@pytest.mark.asyncio
async def test_get_transactions_by_date_range(db_session: AsyncSession):
    """Test getting transactions by date range."""
    # Arrange: Create account and transactions
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create transactions across several days
    today = utc_now().date()
    for i in range(10):
        trans_date = today - timedelta(days=i)
        transaction = TransactionHistory(
            account_id=account.id,
            transaction_date=naive_utc_now(),
            description=f"Transaction {i+1}",
            amount=Decimal("-10.00") * (i + 1),
            type=TransactionType.WITHDRAWAL,
            balance_after=Decimal("1000.00") - (Decimal("10.00") * (i + 1)),
            category="Test",
        )
        db_session.add(transaction)

    await db_session.commit()

    # Create transaction service
    service = TransactionService(session=db_session)

    # Act: Get transactions for specific date range (days 3-6)
    start_date = today - timedelta(days=6)
    end_date = today - timedelta(days=3)
    transactions = await service.get_transactions_by_date_range(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Verify transactions in range
    assert len(transactions) == 4  # Days 3, 4, 5, 6

    # Check that all transactions are within the date range
    for transaction in transactions:
        assert transaction.date.date() >= start_date
        assert transaction.date.date() <= end_date

    # Check that transactions are ordered by date (newest first)
    for i in range(len(transactions) - 1):
        assert transactions[i].date >= transactions[i + 1].date


@pytest.mark.asyncio
async def test_get_transactions_by_date_range_empty(db_session: AsyncSession):
    """Test getting transactions for an empty date range."""
    # Arrange: Create account but no transactions
    account = Account(
        name="Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Create transaction service
    service = TransactionService(session=db_session)

    # Act: Get transactions for empty range
    today = utc_now().date()
    start_date = today - timedelta(days=100)
    end_date = today - timedelta(days=90)
    transactions = await service.get_transactions_by_date_range(
        account_id=account.id, start_date=start_date, end_date=end_date
    )

    # Assert: Empty result for range with no transactions
    assert len(transactions) == 0
