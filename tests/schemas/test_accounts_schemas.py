from datetime import datetime
from decimal import Decimal
import pytest
from zoneinfo import ZoneInfo
from pydantic import ValidationError

from src.schemas.accounts import (
    AccountBase,
    AccountCreate,
    AccountUpdate,
    AccountInDB,
    StatementBalanceHistory,
    AccountType
)

def test_account_base_valid():
    """Test valid account base schema"""
    statement_date = datetime.now(ZoneInfo("UTC"))
    account = AccountBase(
        name="Test Account",
        type=AccountType.CHECKING,
        available_balance=Decimal("1000.00"),
        last_statement_date=statement_date
    )
    assert account.name == "Test Account"
    assert account.type == AccountType.CHECKING
    assert account.available_balance == Decimal("1000.00")
    assert account.last_statement_date == statement_date

def test_account_base_invalid_statement_date():
    """Test invalid statement date validation"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Statement date must be timezone-aware"):
        AccountBase(
            name="Test Account",
            type=AccountType.CHECKING,
            last_statement_date=datetime.now()
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Statement date must be in UTC timezone"):
        AccountBase(
            name="Test Account",
            type=AccountType.CHECKING,
            last_statement_date=non_utc_date
        )

def test_account_update_valid():
    """Test valid account update schema"""
    statement_date = datetime.now(ZoneInfo("UTC"))
    update = AccountUpdate(
        name="Updated Account",
        type=AccountType.SAVINGS,
        last_statement_date=statement_date
    )
    assert update.name == "Updated Account"
    assert update.type == AccountType.SAVINGS
    assert update.last_statement_date == statement_date

def test_account_update_invalid_statement_date():
    """Test invalid statement date in update"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Statement date must be timezone-aware"):
        AccountUpdate(
            name="Updated Account",
            last_statement_date=datetime.now()
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Statement date must be in UTC timezone"):
        AccountUpdate(
            name="Updated Account",
            last_statement_date=non_utc_date
        )

def test_account_in_db_valid():
    """Test valid account in DB schema"""
    now = datetime.now(ZoneInfo("UTC"))
    account = AccountInDB(
        id=1,
        name="Test Account",
        type=AccountType.CREDIT,
        available_balance=Decimal("1000.00"),
        created_at=now,
        updated_at=now
    )
    assert account.id == 1
    assert account.name == "Test Account"
    assert account.type == AccountType.CREDIT
    assert account.created_at == now
    assert account.updated_at == now

def test_account_in_db_invalid_timestamps():
    """Test invalid timestamps in DB schema"""
    now = datetime.now(ZoneInfo("UTC"))
    naive_now = datetime.now()

    # Test naive created_at
    with pytest.raises(ValidationError, match="Timestamp must be timezone-aware"):
        AccountInDB(
            id=1,
            name="Test Account",
            type=AccountType.CREDIT,
            created_at=naive_now,
            updated_at=now
        )

    # Test naive updated_at
    with pytest.raises(ValidationError, match="Timestamp must be timezone-aware"):
        AccountInDB(
            id=1,
            name="Test Account",
            type=AccountType.CREDIT,
            created_at=now,
            updated_at=naive_now
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Timestamp must be in UTC timezone"):
        AccountInDB(
            id=1,
            name="Test Account",
            type=AccountType.CREDIT,
            created_at=non_utc,
            updated_at=now
        )

def test_statement_balance_history_valid():
    """Test valid statement balance history schema"""
    now = datetime.now(ZoneInfo("UTC"))
    history = StatementBalanceHistory(
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now
    )
    assert history.statement_date == now
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment == Decimal("25.00")
    assert history.due_date == now

def test_statement_balance_history_invalid_dates():
    """Test invalid dates in statement balance history"""
    now = datetime.now(ZoneInfo("UTC"))
    naive_now = datetime.now()

    # Test naive statement date
    with pytest.raises(ValidationError, match="Date must be timezone-aware"):
        StatementBalanceHistory(
            statement_date=naive_now,
            statement_balance=Decimal("1000.00"),
            due_date=now
        )

    # Test naive due date
    with pytest.raises(ValidationError, match="Date must be timezone-aware"):
        StatementBalanceHistory(
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            due_date=naive_now
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Date must be in UTC timezone"):
        StatementBalanceHistory(
            statement_date=non_utc,
            statement_balance=Decimal("1000.00"),
            due_date=now
        )
