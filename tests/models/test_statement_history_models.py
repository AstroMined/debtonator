from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.statement_history import StatementHistory

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Credit Card",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

async def test_create_statement_history(
    db_session: AsyncSession,
    test_account: Account
):
    """Test creating a statement history record."""
    statement = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=datetime.now(ZoneInfo("UTC")) + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    assert statement.id is not None
    assert statement.account_id == test_account.id
    assert statement.statement_balance == Decimal("500.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert isinstance(statement.statement_date, datetime)
    assert isinstance(statement.due_date, datetime)
    assert isinstance(statement.created_at, datetime)
    assert isinstance(statement.updated_at, datetime)

async def test_statement_history_relationships(
    db_session: AsyncSession,
    test_account: Account
):
    """Test statement history relationships."""
    statement = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=datetime.now(ZoneInfo("UTC")) + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    # Refresh test_account to load specific relationship
    await db_session.refresh(test_account, ['statement_history'])

    # Test account relationship
    assert statement.account is not None
    assert statement.account.id == test_account.id
    assert statement.account.name == test_account.name

    # Test relationship from account side
    assert statement in test_account.statement_history

async def test_statement_history_string_representation(
    db_session: AsyncSession,
    test_account: Account
):
    """Test the string representation of a statement history record."""
    statement_date = datetime.now(ZoneInfo("UTC"))
    statement = StatementHistory(
        account_id=test_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=statement_date + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()

    expected_str = f"<StatementHistory {test_account.id} - {statement_date}>"
    assert str(statement) == expected_str
    assert repr(statement) == expected_str

async def test_statement_history_cascade_delete(
    db_session: AsyncSession,
    test_account: Account
):
    """Test that statement history records are deleted when account is deleted."""
    statement = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=datetime.now(ZoneInfo("UTC")) + timedelta(days=25)
    )
    db_session.add(statement)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_account)
    await db_session.commit()

    # Verify statement record is also deleted
    result = await db_session.get(StatementHistory, statement.id)
    assert result is None

async def test_statement_history_optional_fields(
    db_session: AsyncSession,
    test_account: Account
):
    """Test creating statement history with optional fields."""
    # Create statement without minimum payment and due date
    statement = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")),
        statement_balance=Decimal("500.00")
    )
    db_session.add(statement)
    await db_session.commit()
    await db_session.refresh(statement)

    assert statement.id is not None
    assert statement.minimum_payment is None
    assert statement.due_date is None

async def test_multiple_statement_history(
    db_session: AsyncSession,
    test_account: Account
):
    """Test recording multiple statements for an account."""
    # First statement
    statement1 = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")) - timedelta(days=30),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=datetime.now(ZoneInfo("UTC")) - timedelta(days=5)
    )
    db_session.add(statement1)
    await db_session.commit()

    # Second statement
    statement2 = StatementHistory(
        account_id=test_account.id,
        statement_date=datetime.now(ZoneInfo("UTC")),
        statement_balance=Decimal("600.00"),
        minimum_payment=Decimal("30.00"),
        due_date=datetime.now(ZoneInfo("UTC")) + timedelta(days=25)
    )
    db_session.add(statement2)
    await db_session.commit()

    # Refresh test_account to load specific relationship
    await db_session.refresh(test_account, ['statement_history'])

    # Verify both records exist and are correctly ordered by statement_date
    statements = test_account.statement_history
    assert len(statements) == 2
    assert statements[0].statement_balance == Decimal("500.00")
    assert statements[1].statement_balance == Decimal("600.00")
