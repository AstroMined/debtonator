"""
Tests for statement history schemas.

These tests validate the validation behavior and proper handling of
statement history data with a focus on account integration.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.accounts import AccountResponse
from src.schemas.statement_history import (
    StatementHistoryCreate,
    StatementHistoryUpdate,
    StatementHistoryWithAccount,
)
from src.utils.datetime_utils import days_ago, utc_datetime, utc_now


def test_statement_history_create_valid():
    """Test creating a valid statement history."""
    # Using utc_now for proper timezone handling
    statement_date = utc_now()
    
    history = StatementHistoryCreate(
        account_id=1,
        statement_date=statement_date,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        payment_due_date=statement_date,
    )

    assert history.account_id == 1
    assert history.statement_date == statement_date
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment == Decimal("25.00")
    assert history.payment_due_date == statement_date


def test_statement_history_create_validates_balance():
    """Test validation of statement balance."""
    statement_date = utc_now()
    
    # Test negative balance
    with pytest.raises(ValidationError) as exc_info:
        StatementHistoryCreate(
            account_id=1,
            statement_date=statement_date,
            statement_balance=Decimal("-100.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=statement_date,
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

    # Zero balance is valid
    history = StatementHistoryCreate(
        account_id=1,
        statement_date=statement_date,
        statement_balance=Decimal("0.00"),
        minimum_payment=Decimal("0.00"),
        payment_due_date=statement_date,
    )
    assert history.statement_balance == Decimal("0.00")


def test_statement_history_create_validates_minimum_payment():
    """Test validation of minimum payment."""
    statement_date = utc_now()
    
    # Test negative payment
    with pytest.raises(ValidationError) as exc_info:
        StatementHistoryCreate(
            account_id=1,
            statement_date=statement_date,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("-25.00"),
            payment_due_date=statement_date,
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

    # Test payment larger than balance
    with pytest.raises(ValidationError) as exc_info:
        StatementHistoryCreate(
            account_id=1,
            statement_date=statement_date,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("1100.00"),
            payment_due_date=statement_date,
        )
    assert "Minimum payment cannot exceed statement balance" in str(exc_info.value)

    # Zero minimum payment is valid
    history = StatementHistoryCreate(
        account_id=1,
        statement_date=statement_date,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("0.00"),
        payment_due_date=statement_date,
    )
    assert history.minimum_payment == Decimal("0.00")


def test_statement_history_create_validates_dates():
    """Test validation of statement and payment dates."""
    now = utc_now()
    
    # Test due date before statement date
    with pytest.raises(ValidationError) as exc_info:
        StatementHistoryCreate(
            account_id=1,
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("25.00"),
            payment_due_date=days_ago(10),  # 10 days before now
        )
    assert "Payment due date cannot be before statement date" in str(exc_info.value)

    # Test same dates (valid)
    history = StatementHistoryCreate(
        account_id=1,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        payment_due_date=now,
    )
    assert history.statement_date == history.payment_due_date


def test_statement_history_update_valid():
    """Test updating a statement history."""
    # Using utc_now for proper timezone handling
    due_date = utc_now()
    
    update = StatementHistoryUpdate(
        minimum_payment=Decimal("35.00"),
        payment_due_date=due_date,
    )

    assert update.minimum_payment == Decimal("35.00")
    assert update.payment_due_date == due_date
    assert update.statement_balance is None  # Not updated


def test_statement_history_update_partial():
    """Test partial updates with validation."""
    # Using utc_now for proper timezone handling
    due_date = utc_now()
    
    # Update just minimum payment
    update1 = StatementHistoryUpdate(minimum_payment=Decimal("35.00"))
    assert update1.minimum_payment == Decimal("35.00")
    assert update1.payment_due_date is None

    # Update just payment due date
    update2 = StatementHistoryUpdate(payment_due_date=due_date)
    assert update2.payment_due_date == due_date
    assert update2.minimum_payment is None


def test_statement_history_with_account_valid():
    """Test StatementHistoryWithAccount schema."""
    now = utc_now()
    
    # Create account response with all required fields including account_type
    account = AccountResponse(
        id=2,
        name="Test Account",
        current_balance=Decimal("2000.00"),
        available_balance=Decimal("1900.00"),
        account_type="credit",  # Required field
        created_at=now,
        updated_at=now,
    )
    
    # Create statement history
    history = StatementHistoryWithAccount(
        id=1,
        account_id=2,
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        payment_due_date=now,
        is_paid=False,
        created_at=now,
        updated_at=now,
        account=account,
    )

    # Verify the joined data is correct
    assert history.id == 1
    assert history.account_id == 2
    assert history.statement_date == now
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment == Decimal("25.00")
    assert history.payment_due_date == now
    assert history.is_paid is False
    assert history.account.id == 2
    assert history.account.name == "Test Account"
    assert history.account.current_balance == Decimal("2000.00")
    assert history.account.account_type == "credit"  # Properly included
