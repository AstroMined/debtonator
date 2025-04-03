from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.accounts import AccountResponse
from src.schemas.statement_history import (
    StatementHistory,
    StatementHistoryBase,
    StatementHistoryCreate,
    StatementHistoryResponse,
    StatementHistoryTrend,
    StatementHistoryUpdate,
    StatementHistoryWithAccount,
    UpcomingStatementDue,
)


def test_statement_history_base_valid():
    """Test valid statement history base schema"""
    statement_date = datetime.now(timezone.utc)
    due_date = statement_date + timedelta(days=30)

    statement = StatementHistoryBase(
        account_id=1,
        statement_date=statement_date,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=due_date,
    )

    assert statement.account_id == 1
    assert statement.statement_date == statement_date
    assert statement.statement_balance == Decimal("1000.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert statement.due_date == due_date


def test_statement_history_base_required_fields():
    """Test statement history base required fields"""
    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        StatementHistoryBase(
            statement_date=datetime.now(timezone.utc),
            statement_balance=Decimal("1000.00"),
        )

    # Test missing statement_date
    with pytest.raises(ValidationError, match="Field required"):
        StatementHistoryBase(
            account_id=1,
            statement_balance=Decimal("1000.00"),
        )

    # Test missing statement_balance
    with pytest.raises(ValidationError, match="Field required"):
        StatementHistoryBase(
            account_id=1,
            statement_date=datetime.now(timezone.utc),
        )

    # Test with only required fields
    statement = StatementHistoryBase(
        account_id=1,
        statement_date=datetime.now(timezone.utc),
        statement_balance=Decimal("1000.00"),
    )
    assert statement.minimum_payment is None
    assert statement.due_date is None


def test_statement_history_test_checking_account_id_validation():
    """Test account_id field validation"""
    # Test invalid account_id (less than or equal to 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        StatementHistoryBase(
            account_id=0,
            statement_date=datetime.now(timezone.utc),
            statement_balance=Decimal("1000.00"),
        )


def test_statement_history_base_decimal_validation():
    """Test decimal field validation"""
    now = datetime.now(timezone.utc)

    # Test statement_balance with too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        StatementHistoryBase(
            account_id=1,
            statement_date=now,
            statement_balance=Decimal("1000.123"),
        )

    # Test minimum_payment with too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        StatementHistoryBase(
            account_id=1,
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.123"),
        )

    # Test negative minimum_payment
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        StatementHistoryBase(
            account_id=1,
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("-25.00"),
        )

    # Test valid decimal formats
    statement1 = StatementHistoryBase(
        account_id=1,
        statement_date=now,
        statement_balance=Decimal("1000"),  # 0 decimal places
    )
    assert statement1.statement_balance == Decimal("1000")

    statement2 = StatementHistoryBase(
        account_id=1,
        statement_date=now,
        statement_balance=Decimal("1000.5"),  # 1 decimal place
    )
    assert statement2.statement_balance == Decimal("1000.5")

    statement3 = StatementHistoryBase(
        account_id=1,
        statement_date=now,
        statement_balance=Decimal("1000.50"),  # 2 decimal places
    )
    assert statement3.statement_balance == Decimal("1000.50")


def test_statement_history_base_datetime_validation():
    """Test datetime field validation"""
    now_naive = datetime.now()
    now_utc = datetime.now(timezone.utc)

    # Test naive statement_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementHistoryBase(
            account_id=1,
            statement_date=now_naive,
            statement_balance=Decimal("1000.00"),
        )

    # Test naive due_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementHistoryBase(
            account_id=1,
            statement_date=now_utc,
            statement_balance=Decimal("1000.00"),
            due_date=now_naive,
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementHistoryBase(
            account_id=1,
            statement_date=non_utc_date,
            statement_balance=Decimal("1000.00"),
        )


def test_statement_history_create_valid():
    """Test valid statement history create schema"""
    now = datetime.now(timezone.utc)

    # StatementHistoryCreate should behave like StatementHistoryBase
    statement = StatementHistoryCreate(
        account_id=1,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now + timedelta(days=30),
    )

    assert statement.account_id == 1
    assert statement.statement_date == now
    assert statement.statement_balance == Decimal("1000.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert statement.due_date == now + timedelta(days=30)


def test_statement_history_update_valid():
    """Test valid statement history update schema"""
    now = datetime.now(timezone.utc)

    # Test partial update with only some fields
    update = StatementHistoryUpdate(
        statement_balance=Decimal("1500.00"),
        minimum_payment=Decimal("30.00"),
    )

    assert update.account_id is None
    assert update.statement_date is None
    assert update.statement_balance == Decimal("1500.00")
    assert update.minimum_payment == Decimal("30.00")
    assert update.due_date is None

    # Test complete update with all fields
    full_update = StatementHistoryUpdate(
        account_id=2,
        statement_date=now,
        statement_balance=Decimal("2000.00"),
        minimum_payment=Decimal("40.00"),
        due_date=now + timedelta(days=30),
    )

    assert full_update.account_id == 2
    assert full_update.statement_date == now
    assert full_update.statement_balance == Decimal("2000.00")
    assert full_update.minimum_payment == Decimal("40.00")
    assert full_update.due_date == now + timedelta(days=30)


def test_statement_history_update_validation():
    """Test statement history update validation"""
    # Test account_id validation
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        StatementHistoryUpdate(account_id=0)

    # Test statement_balance decimal validation
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        StatementHistoryUpdate(statement_balance=Decimal("1000.123"))

    # Test minimum_payment range validation
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        StatementHistoryUpdate(minimum_payment=Decimal("-25.00"))

    # Test datetime validation
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementHistoryUpdate(statement_date=datetime.now())


def test_statement_history_valid():
    """Test valid statement history schema"""
    now = datetime.now(timezone.utc)

    statement = StatementHistory(
        id=1,
        account_id=2,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now + timedelta(days=30),
    )

    assert statement.id == 1
    assert statement.account_id == 2
    assert statement.statement_date == now
    assert statement.statement_balance == Decimal("1000.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert statement.due_date == now + timedelta(days=30)


def test_statement_history_id_validation():
    """Test statement history ID validation"""
    now = datetime.now(timezone.utc)

    # Test invalid ID
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        StatementHistory(
            id=0,
            account_id=2,
            statement_date=now,
            statement_balance=Decimal("1000.00"),
        )


def test_statement_history_with_account_valid():
    """Test valid statement history with account schema"""
    now = datetime.now(timezone.utc)

    # Create mock account response
    account = AccountResponse(
        id=2,
        name="Test Account",
        type="credit",
        available_balance=Decimal("5000.00"),
        created_at=now,
        updated_at=now,
    )

    # Create statement with account
    statement = StatementHistoryWithAccount(
        id=1,
        account_id=2,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now + timedelta(days=30),
        account=account,
    )

    assert statement.id == 1
    assert statement.account_id == 2
    assert statement.account.id == 2
    assert statement.account.name == "Test Account"


def test_statement_history_with_account_validation():
    """Test statement history with account validation"""
    now = datetime.now(timezone.utc)

    # Missing account field
    with pytest.raises(ValidationError, match="Field required"):
        StatementHistoryWithAccount(
            id=1,
            account_id=2,
            statement_date=now,
            statement_balance=Decimal("1000.00"),
        )


def test_statement_history_response_valid():
    """Test valid statement history response schema"""
    now = datetime.now(timezone.utc)

    # Should behave like StatementHistory
    response = StatementHistoryResponse(
        id=1,
        account_id=2,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now + timedelta(days=30),
    )

    assert response.id == 1
    assert response.account_id == 2
    assert response.statement_date == now
    assert response.statement_balance == Decimal("1000.00")


def test_statement_history_trend_valid():
    """Test valid statement history trend schema"""
    now = datetime.now(timezone.utc)
    dates = [now - timedelta(days=i * 30) for i in range(3)]
    balances = [Decimal("1000.00"), Decimal("1200.00"), Decimal("900.00")]
    payments = [Decimal("25.00"), Decimal("30.00"), None]

    trend = StatementHistoryTrend(
        account_id=1,
        statement_dates=dates,
        statement_balances=balances,
        minimum_payments=payments,
    )

    assert trend.account_id == 1
    assert len(trend.statement_dates) == 3
    assert len(trend.statement_balances) == 3
    assert len(trend.minimum_payments) == 3
    assert trend.minimum_payments[2] is None


def test_statement_history_trend_validation():
    """Test statement history trend validation"""
    now = datetime.now(timezone.utc)
    dates = [now - timedelta(days=i * 30) for i in range(3)]
    balances = [Decimal("1000.00"), Decimal("1200.00"), Decimal("900.00")]
    payments = [Decimal("25.00"), Decimal("30.00")]  # One less than dates

    # Test account_id validation
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        StatementHistoryTrend(
            account_id=0,
            statement_dates=dates,
            statement_balances=balances,
            minimum_payments=payments,
        )

    # Lists should be provided
    with pytest.raises(ValidationError):
        StatementHistoryTrend(
            account_id=1,
            statement_dates="not a list",  # type: ignore
            statement_balances=balances,
            minimum_payments=payments,
        )

    # Decimal validation in lists
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        StatementHistoryTrend(
            account_id=1,
            statement_dates=dates,
            statement_balances=[Decimal("1000.123")],  # Too many decimal places
            minimum_payments=payments,
        )


def test_upcoming_statement_due_valid():
    """Test valid upcoming statement due schema"""
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(days=5)

    upcoming = UpcomingStatementDue(
        statement_id=1,
        account_id=2,
        account_name="Test Account",
        due_date=due_date,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        days_until_due=5,
    )

    assert upcoming.statement_id == 1
    assert upcoming.account_id == 2
    assert upcoming.account_name == "Test Account"
    assert upcoming.due_date == due_date
    assert upcoming.statement_balance == Decimal("1000.00")
    assert upcoming.minimum_payment == Decimal("25.00")
    assert upcoming.days_until_due == 5


def test_upcoming_statement_due_validation():
    """Test upcoming statement due validation"""
    now = datetime.now(timezone.utc)

    # Test ID validation
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        UpcomingStatementDue(
            statement_id=0,
            account_id=2,
            account_name="Test Account",
            due_date=now,
            statement_balance=Decimal("1000.00"),
            days_until_due=5,
        )

    # Test decimal validation
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        UpcomingStatementDue(
            statement_id=1,
            account_id=2,
            account_name="Test Account",
            due_date=now,
            statement_balance=Decimal("1000.123"),  # Too many decimal places
            days_until_due=5,
        )

    # Test minimum_payment validation
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        UpcomingStatementDue(
            statement_id=1,
            account_id=2,
            account_name="Test Account",
            due_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("-25.00"),  # Negative value
            days_until_due=5,
        )
