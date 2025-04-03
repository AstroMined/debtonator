from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.models.statement_history import StatementHistory
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_create_statement_history(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test creating a statement history record."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25),
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    assert statement.id is not None
    assert statement.account_id == test_credit_account.id
    assert statement.statement_balance == Decimal("500.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert isinstance(statement.statement_date, datetime)
    assert isinstance(statement.due_date, datetime)
    assert isinstance(statement.created_at, datetime)
    assert isinstance(statement.updated_at, datetime)


async def test_statement_history_relationships(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test statement history relationships."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25),
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ["statement_history"])

    # Test account relationship
    assert statement.account is not None
    assert statement.account.id == test_credit_account.id
    assert statement.account.name == test_credit_account.name

    # Test relationship from account side
    assert statement in test_credit_account.statement_history


async def test_statement_history_string_representation(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test the string representation of a statement history record."""
    statement_date = naive_utc_now()
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=statement_date + timedelta(days=25),
    )
    db_session.add(statement)
    await db_session.commit()

    expected_str = f"<StatementHistory {test_credit_account.id} - {statement_date}>"
    assert str(statement) == expected_str
    assert repr(statement) == expected_str


async def test_statement_history_cascade_delete(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test that statement history records are deleted when account is deleted."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25),
    )
    db_session.add(statement)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_credit_account)
    await db_session.commit()

    # Verify statement record is also deleted
    result = await db_session.get(StatementHistory, statement.id)
    assert result is None


async def test_statement_history_due_date_field(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test due date as a regular field in statement history model."""
    statement_date = naive_utc_now()

    # Test explicit due date
    explicit_due_date = naive_utc_now() + timedelta(days=30)
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("600.00"),
        due_date=explicit_due_date,
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    # Due date should be stored as provided
    assert statement.due_date == explicit_due_date

    # Verify model allows due_date to be null since calculation
    # is now handled by the service layer
    statement2 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("700.00"),
        due_date=None,
    )
    db_session.add(statement2)
    await db_session.commit()
    await db_session.refresh(statement2)

    # Due date can be null in model (will be calculated in service)
    assert statement2.due_date is None


async def test_multiple_statement_history(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test recording multiple statements for an account."""
    # First statement
    statement1 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now() - timedelta(days=30),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() - timedelta(days=5),
    )
    db_session.add(statement1)
    await db_session.commit()

    # Second statement
    statement2 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("600.00"),
        minimum_payment=Decimal("30.00"),
        due_date=naive_utc_now() + timedelta(days=25),
    )
    db_session.add(statement2)
    await db_session.commit()

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ["statement_history"])

    # Verify both records exist and are correctly ordered by statement_date
    statements = test_credit_account.statement_history
    assert len(statements) == 2
    assert statements[0].statement_balance == Decimal("500.00")
    assert statements[1].statement_balance == Decimal("600.00")


async def test_datetime_handling(
    db_session: AsyncSession, test_credit_account: CreditAccount
):
    """Test proper datetime handling in statement history"""
    # Create statement with explicit datetime values
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_from_date(2025, 3, 15),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_from_date(2025, 4, 10),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    # Verify all datetime fields are naive (no tzinfo)
    assert statement.statement_date.tzinfo is None
    assert statement.due_date.tzinfo is None
    assert statement.created_at.tzinfo is None
    assert statement.updated_at.tzinfo is None

    # Verify statement_date components
    assert statement.statement_date.year == 2025
    assert statement.statement_date.month == 3
    assert statement.statement_date.day == 15
    assert statement.statement_date.hour == 0
    assert statement.statement_date.minute == 0
    assert statement.statement_date.second == 0

    # Verify due_date components
    assert statement.due_date.year == 2025
    assert statement.due_date.month == 4
    assert statement.due_date.day == 10
    assert statement.due_date.hour == 0
    assert statement.due_date.minute == 0
    assert statement.due_date.second == 0
