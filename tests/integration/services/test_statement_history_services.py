from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_now
from src.models.statement_history import StatementHistory
from src.services.statement_history import StatementService

pytestmark = pytest.mark.asyncio


async def test_calculate_due_date(db_session: AsyncSession):
    """Test the calculate_due_date method."""
    service = StatementService(db_session)

    # Test with current date
    now = naive_utc_now()
    due_date = service.calculate_due_date(now)

    # Verify due date is 25 days after statement date
    assert due_date == now + timedelta(days=25)

    # Test with specific date
    statement_date = datetime(2025, 3, 15)
    due_date = service.calculate_due_date(statement_date)

    # Verify due date is correct
    assert due_date.year == 2025
    assert due_date.month == 4
    assert due_date.day == 9  # March 15 + 25 days = April 9

    # Verify time components remain the same
    assert due_date.hour == statement_date.hour
    assert due_date.minute == statement_date.minute
    assert due_date.second == statement_date.second


async def test_create_statement(db_session: AsyncSession, test_credit_account: Account):
    """Test creating a statement via the service."""
    service = StatementService(db_session)
    statement_date = naive_utc_now()

    # Create statement without providing due_date
    statement = await service.create_statement(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
    )

    # Add to session and commit
    await db_session.commit()
    await db_session.refresh(statement)

    # Verify statement was created
    assert statement.id is not None
    assert statement.account_id == test_credit_account.id
    assert statement.statement_date == statement_date
    assert statement.statement_balance == Decimal("500.00")
    assert statement.minimum_payment == Decimal("25.00")

    # Verify due date was calculated
    assert statement.due_date == statement_date + timedelta(days=25)

    # Verify account relationship
    assert statement.account is not None
    assert statement.account.id == test_credit_account.id


async def test_create_statement_with_explicit_due_date(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test creating a statement with an explicitly provided due date."""
    service = StatementService(db_session)
    statement_date = naive_utc_now()
    explicit_due_date = statement_date + timedelta(days=30)  # Custom due date

    # Create statement with explicit due_date
    statement = await service.create_statement(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("600.00"),
        minimum_payment=Decimal("30.00"),
        due_date=explicit_due_date,
    )

    await db_session.commit()
    await db_session.refresh(statement)

    # Verify due date matches what was provided
    assert statement.due_date == explicit_due_date
    assert statement.due_date != statement_date + timedelta(days=25)  # Not the default


async def test_create_statement_nonexistent_account(db_session: AsyncSession):
    """Test creating a statement for a nonexistent account."""
    service = StatementService(db_session)
    statement_date = naive_utc_now()

    # Attempt to create statement for nonexistent account
    with pytest.raises(ValueError, match="Account with ID 9999 not found"):
        await service.create_statement(
            account_id=9999,  # Non-existent account ID
            statement_date=statement_date,
            statement_balance=Decimal("500.00"),
        )


async def test_get_statement(db_session: AsyncSession, test_credit_account: Account):
    """Test getting a statement by ID."""
    # Create a statement directly
    statement = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("500.00"),
    )
    db_session.add(statement)
    await db_session.commit()

    # Retrieve via service
    service = StatementService(db_session)
    retrieved = await service.get_statement(statement.id)

    # Verify retrieval
    assert retrieved is not None
    assert retrieved.id == statement.id
    assert retrieved.account_id == test_credit_account.id
    assert retrieved.statement_balance == Decimal("500.00")


async def test_get_account_statements(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test getting statements for an account."""
    # Create several statements with different dates
    statement1 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now() - timedelta(days=60),
        statement_balance=Decimal("500.00"),
    )
    statement2 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now() - timedelta(days=30),
        statement_balance=Decimal("600.00"),
    )
    statement3 = StatementHistory(
        account_id=test_credit_account.id,
        statement_date=naive_utc_now(),
        statement_balance=Decimal("700.00"),
    )

    db_session.add_all([statement1, statement2, statement3])
    await db_session.commit()

    # Retrieve via service
    service = StatementService(db_session)
    statements = await service.get_account_statements(test_credit_account.id)

    # Verify retrieval and ordering (newest first)
    assert len(statements) == 3
    assert statements[0].id == statement3.id  # Most recent first
    assert statements[1].id == statement2.id
    assert statements[2].id == statement1.id  # Oldest last

    # Test with limit
    limited = await service.get_account_statements(test_credit_account.id, limit=2)
    assert len(limited) == 2
    assert limited[0].id == statement3.id
    assert limited[1].id == statement2.id


async def test_get_account_statements_empty(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test getting statements for an account with no statements."""
    service = StatementService(db_session)

    # Account exists but has no statements
    statements = await service.get_account_statements(test_checking_account.id)

    # Should return empty list, not None
    assert statements is not None
    assert isinstance(statements, list)
    assert len(statements) == 0


async def test_datetime_handling(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test proper UTC naive datetime handling in service."""
    service = StatementService(db_session)

    # Create with explicit datetime
    statement_date = datetime(2025, 3, 15, 0, 0, 0)
    statement = await service.create_statement(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
    )

    await db_session.commit()
    await db_session.refresh(statement)

    # Verify all datetime fields are naive
    assert statement.statement_date.tzinfo is None
    assert statement.due_date.tzinfo is None
    assert statement.created_at.tzinfo is None
    assert statement.updated_at.tzinfo is None

    # Verify correct date calculations
    assert statement.statement_date.year == 2025
    assert statement.statement_date.month == 3
    assert statement.statement_date.day == 15

    # Due date should be 25 days after statement date
    assert statement.due_date.year == 2025
    assert statement.due_date.month == 4
    assert statement.due_date.day == 9
