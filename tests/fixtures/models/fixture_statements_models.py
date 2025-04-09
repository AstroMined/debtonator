from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Tuple

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.credit_limit_history import CreditLimitHistory
from src.models.statement_history import StatementHistory
from src.utils.datetime_utils import utc_now


@pytest_asyncio.fixture
async def test_statement_history(
    db_session: AsyncSession,
    test_credit_account,
) -> StatementHistory:
    """Create a test statement history entry for a credit account."""
    # Create naive datetimes for DB storage
    statement_date = (utc_now() - timedelta(days=15)).replace(tzinfo=None)
    due_date = (utc_now() + timedelta(days=15)).replace(tzinfo=None)

    # Create model instance directly
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=due_date,
    )

    # Add to session manually
    db_session.add(statement)
    await db_session.flush()
    await db_session.refresh(statement)

    return statement


@pytest_asyncio.fixture
async def test_multiple_statements(
    db_session: AsyncSession,
    test_credit_account,
) -> List[StatementHistory]:
    """Create multiple statement history records for use in tests."""
    # Setup statement configurations
    now = utc_now()
    statement_configs = [
        (
            now - timedelta(days=60),
            Decimal("400.00"),
            Decimal("20.00"),
            now - timedelta(days=39),
        ),
        (
            now - timedelta(days=30),
            Decimal("600.00"),
            Decimal("30.00"),
            now - timedelta(days=9),
        ),
        (now, Decimal("800.00"), Decimal("40.00"), now + timedelta(days=21)),
    ]

    statements = []
    for stmt_date, balance, min_payment, due_date in statement_configs:
        # Make datetimes naive for DB storage
        naive_stmt_date = stmt_date.replace(tzinfo=None)
        naive_due_date = due_date.replace(tzinfo=None)

        # Create model instance directly
        statement = StatementHistory(
            account_id=test_credit_account.id,
            statement_date=naive_stmt_date,
            statement_balance=balance,
            minimum_payment=min_payment,
            due_date=naive_due_date,
        )

        # Add to session manually
        db_session.add(statement)
        statements.append(statement)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for statement in statements:
        await db_session.refresh(statement)

    return statements


@pytest_asyncio.fixture
async def test_multiple_accounts_with_statements(
    db_session: AsyncSession,
) -> Tuple[List[Account], List[StatementHistory]]:
    """Create multiple accounts with statements for testing."""
    # Setup account configurations
    accounts = []
    statements = []
    now = utc_now()

    # Create two credit accounts
    for i in range(2):
        # Create account model instance directly
        account = Account(
            name=f"Credit Account {i+1}",
            type="credit",
            available_balance=Decimal(f"-{(i+5)*100}.00"),
            total_limit=Decimal(f"{(i+1)*1000}.00"),
            available_credit=Decimal(f"{(i+1)*1000 - (i+5)*100}.00"),
        )

        # Add to session manually
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        accounts.append(account)

        # Create statements for each account
        for j in range(3):
            days_offset = (3 - j) * 30  # 90, 60, 30 days ago
            # Make datetimes naive for DB storage
            stmt_date = (now - timedelta(days=days_offset)).replace(tzinfo=None)
            due_date = (now - timedelta(days=days_offset - 21)).replace(
                tzinfo=None
            )  # Due 21 days after statement

            # Create statement model instance directly
            statement = StatementHistory(
                account_id=account.id,
                statement_date=stmt_date,
                statement_balance=Decimal(f"{(i+j+1)*200}.00"),
                minimum_payment=Decimal(f"{(i+j+1)*10}.00"),
                due_date=due_date,
            )

            # Add to session manually
            db_session.add(statement)
            await db_session.flush()
            await db_session.refresh(statement)
            statements.append(statement)

        # Create additional statements with future due dates (needed for tests checking upcoming due dates)
        for j in range(3):
            days_future = (j + 1) * 10  # 10, 20, 30 days in future
            # Make datetimes naive for DB storage
            stmt_date = (now - timedelta(days=30 - j * 10)).replace(
                tzinfo=None
            )  # Statements from past 30 days
            due_date = (now + timedelta(days=days_future)).replace(
                tzinfo=None
            )  # Due dates in the future

            # Create statement model instance directly
            statement = StatementHistory(
                account_id=account.id,
                statement_date=stmt_date,
                statement_balance=Decimal(
                    f"{(i+j+4)*200}.00"
                ),  # Continue the sequence from previous statements
                minimum_payment=Decimal(
                    f"{(i+j+4)*10}.00"
                ),  # Continue the sequence from previous statements
                due_date=due_date,
            )

            # Add to session manually
            db_session.add(statement)
            await db_session.flush()
            await db_session.refresh(statement)
            statements.append(statement)

    return accounts, statements


@pytest_asyncio.fixture
async def test_credit_limit_history(
    db_session: AsyncSession,
    test_credit_account,
) -> CreditLimitHistory:
    """Create a test credit limit history entry for use in tests."""
    # Create a naive datetime for DB storage
    effective_date = utc_now().replace(tzinfo=None)

    # Create model instance directly
    credit_limit = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("3000.00"),
        reason="Credit limit increase",
        effective_date=effective_date,
    )

    # Add to session manually
    db_session.add(credit_limit)
    await db_session.flush()
    await db_session.refresh(credit_limit)

    return credit_limit


@pytest_asyncio.fixture
async def test_credit_limit_changes(
    db_session: AsyncSession,
    test_credit_account,
) -> List[CreditLimitHistory]:
    """Create multiple credit limit history entries for testing."""
    now = datetime.now(timezone.utc)

    # Create base entry
    base_date = (now - timedelta(days=90)).replace(tzinfo=None)
    base_entry = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("5000.00"),
        effective_date=base_date,
        reason="Initial credit limit",
    )
    db_session.add(base_entry)
    await db_session.flush()

    # Create increase entry
    increase_date = (now - timedelta(days=60)).replace(tzinfo=None)
    increase = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("7500.00"),
        effective_date=increase_date,
        reason="Credit increase due to good payment history",
    )
    db_session.add(increase)
    await db_session.flush()

    # Create decrease entry
    decrease_date = (now - timedelta(days=30)).replace(tzinfo=None)
    decrease = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("6500.00"),
        effective_date=decrease_date,
        reason="Credit adjustment due to risk assessment",
    )
    db_session.add(decrease)
    await db_session.flush()

    # Create recent increase entry
    latest_date = (now - timedelta(days=5)).replace(tzinfo=None)
    latest = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("8000.00"),
        effective_date=latest_date,
        reason="Credit increase request approved",
    )
    db_session.add(latest)
    await db_session.flush()

    # Refresh all entries
    await db_session.refresh(increase)
    await db_session.refresh(decrease)
    await db_session.refresh(latest)

    return [increase, decrease, latest]
