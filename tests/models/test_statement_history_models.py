from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.models.base_model import naive_utc_now, naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_create_statement_history(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test creating a statement history record."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25)
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
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test statement history relationships."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ['statement_history'])

    # Test account relationship
    assert statement.account is not None
    assert statement.account.id == test_credit_account.id
    assert statement.account.name == test_credit_account.name

    # Test relationship from account side
    assert statement in test_credit_account.statement_history

async def test_statement_history_string_representation(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test the string representation of a statement history record."""
    statement_date = naive_utc_now()
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=statement_date + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()

    expected_str = f"<StatementHistory {test_credit_account.id} - {statement_date}>"
    assert str(statement) == expected_str
    assert repr(statement) == expected_str

async def test_statement_history_cascade_delete(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test that statement history records are deleted when account is deleted."""
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_credit_account)
    await db_session.commit()

    # Verify statement record is also deleted
    result = await db_session.get(StatementHistory, statement.id)
    assert result is None

async def test_statement_history_due_date_handling(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test due date handling in statement history."""
    statement_date = naive_utc_now()

    # Test 1: Default due date (25 days from statement date)
    statement1 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00")
    )
    db_session.add(statement1)
    await db_session.commit()
    await db_session.refresh(statement1)

    assert statement1.id is not None
    assert statement1.due_date is not None
    assert statement1.due_date == statement_date + timedelta(days=25)
    assert statement1.minimum_payment is None  # Minimum payment remains optional

    # Test 2: Explicit due date
    explicit_due_date = naive_utc_now() + timedelta(days=30)
    statement2 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("600.00"),
        due_date=explicit_due_date
    )
    db_session.add(statement2)
    await db_session.commit()
    await db_session.refresh(statement2)

    assert statement2.due_date == explicit_due_date

    # Test 3: Explicitly set due date to None
    statement3 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("700.00"),
        due_date=None
    )
    db_session.add(statement3)
    await db_session.commit()
    await db_session.refresh(statement3)

    assert statement3.due_date is None

async def test_multiple_statement_history(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test recording multiple statements for an account."""
    # First statement
    statement1 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now() - timedelta(days=30),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=naive_utc_now() - timedelta(days=5)
    )
    db_session.add(statement1)
    await db_session.commit()

    # Second statement
    statement2 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("600.00"),
        minimum_payment=Decimal("30.00"),
        due_date=naive_utc_now() + timedelta(days=25)
    )
    db_session.add(statement2)
    await db_session.commit()

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ['statement_history'])

    # Verify both records exist and are correctly ordered by statement_date
    statements = test_credit_account.statement_history
    assert len(statements) == 2
    assert statements[0].statement_balance == Decimal("500.00")
    assert statements[1].statement_balance == Decimal("600.00")

async def test_datetime_handling(
    db_session: AsyncSession,
    test_credit_account: Account
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
        updated_at=naive_utc_now()
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
