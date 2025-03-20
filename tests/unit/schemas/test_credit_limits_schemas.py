from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.credit_limit_history import (
    AccountCreditLimitHistoryResponse,
    CreditLimitHistoryBase,
    CreditLimitHistoryCreate,
    CreditLimitHistoryInDB,
    CreditLimitHistoryUpdate,
)


# Test valid object creation
def test_credit_limit_history_base_valid():
    """Test valid credit limit history base schema"""
    now = datetime.now(timezone.utc)

    data = CreditLimitHistoryBase(
        credit_limit=Decimal("5000.00"),
        effective_date=now,
        reason="Initial credit limit",
    )

    assert data.credit_limit == Decimal("5000.00")
    assert data.effective_date == now
    assert data.reason == "Initial credit limit"


def test_credit_limit_history_base_minimal():
    """Test minimal credit limit history base schema"""
    now = datetime.now(timezone.utc)

    data = CreditLimitHistoryBase(credit_limit=Decimal("5000.00"), effective_date=now)

    assert data.credit_limit == Decimal("5000.00")
    assert data.effective_date == now
    assert data.reason is None


def test_credit_limit_history_create_valid():
    """Test valid credit limit history create schema"""
    now = datetime.now(timezone.utc)

    data = CreditLimitHistoryCreate(
        account_id=1,  # Add required account_id field
        credit_limit=Decimal("5000.00"),
        effective_date=now,
        reason="Initial credit limit",
    )

    assert data.credit_limit == Decimal("5000.00")
    assert data.effective_date == now
    assert data.reason == "Initial credit limit"


def test_credit_limit_history_in_db_valid():
    """Test valid credit limit history in DB schema"""
    now = datetime.now(timezone.utc)

    data = CreditLimitHistoryInDB(
        id=1,
        account_id=2,
        credit_limit=Decimal("5000.00"),
        effective_date=now,
        reason="Initial credit limit",
        created_at=now,
    )

    assert data.id == 1
    assert data.account_id == 2
    assert data.credit_limit == Decimal("5000.00")
    assert data.effective_date == now
    assert data.reason == "Initial credit limit"
    assert data.created_at == now


def test_credit_limit_history_update_valid():
    """Test valid credit limit update schema"""
    now = datetime.now(timezone.utc)

    data = CreditLimitHistoryUpdate(
        id=1,  # Add required id field
        credit_limit=Decimal("7500.00"),
        effective_date=now,
        reason="Increased credit limit due to good payment history",
    )

    assert data.credit_limit == Decimal("7500.00")
    assert data.effective_date == now
    assert data.reason == "Increased credit limit due to good payment history"


def test_account_credit_limit_history_response_valid():
    """Test valid account credit limit history response schema"""
    now = datetime.now(timezone.utc)

    # Create history entries
    history1 = CreditLimitHistoryInDB(
        id=1,
        account_id=2,
        credit_limit=Decimal("5000.00"),
        effective_date=now.replace(year=now.year - 1),  # Last year
        reason="Initial credit limit",
        created_at=now.replace(year=now.year - 1),
    )

    history2 = CreditLimitHistoryInDB(
        id=2,
        account_id=2,
        credit_limit=Decimal("7500.00"),
        effective_date=now,
        reason="Increased credit limit",
        created_at=now,
    )

    # Create response with history
    response = AccountCreditLimitHistoryResponse(
        account_id=2,
        account_name="Test Credit Card",
        current_credit_limit=Decimal("7500.00"),
        credit_limit_history=[history1, history2],
    )

    assert response.account_id == 2
    assert response.account_name == "Test Credit Card"
    assert response.current_credit_limit == Decimal("7500.00")
    assert len(response.credit_limit_history) == 2
    assert response.credit_limit_history[0].credit_limit == Decimal("5000.00")
    assert response.credit_limit_history[1].credit_limit == Decimal("7500.00")


# Test field validations
def test_credit_limit_validation():
    """Test credit limit field validation"""
    now = datetime.now(timezone.utc)

    # Test credit limit must be greater than zero
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        CreditLimitHistoryBase(credit_limit=Decimal("0.00"), effective_date=now)

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        CreditLimitHistoryBase(credit_limit=Decimal("-100.00"), effective_date=now)

    # Test valid credit limit at the boundary
    data = CreditLimitHistoryBase(
        credit_limit=Decimal("0.01"), effective_date=now  # Just above zero
    )
    assert data.credit_limit == Decimal("0.01")


def test_reason_validation():
    """Test reason field validation"""
    now = datetime.now(timezone.utc)

    # Test reason max length
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        CreditLimitHistoryBase(
            credit_limit=Decimal("5000.00"),
            effective_date=now,
            reason="X" * 501,  # 501 characters
        )

    # Test valid reason at the boundary
    data = CreditLimitHistoryBase(
        credit_limit=Decimal("5000.00"),
        effective_date=now,
        reason="X" * 500,  # 500 characters
    )
    assert len(data.reason) == 500


def test_required_fields():
    """Test required fields validation"""
    now = datetime.now(timezone.utc)

    # Test missing credit_limit
    with pytest.raises(ValidationError, match="Field required"):
        CreditLimitHistoryBase(effective_date=now)

    # Test missing effective_date
    with pytest.raises(ValidationError, match="Field required"):
        CreditLimitHistoryBase(credit_limit=Decimal("5000.00"))

    # Test missing id and account_id in DB schema
    with pytest.raises(ValidationError, match="Field required"):
        CreditLimitHistoryInDB(
            credit_limit=Decimal("5000.00"), effective_date=now, created_at=now
        )

    with pytest.raises(ValidationError, match="Field required"):
        CreditLimitHistoryInDB(
            id=1, credit_limit=Decimal("5000.00"), effective_date=now, created_at=now
        )


# Test decimal precision
def test_decimal_precision():
    """Test decimal precision validation"""
    now = datetime.now(timezone.utc)

    # Test too many decimal places
    with pytest.raises(
        ValidationError, match="Input should be a multiple of 0.01"
    ):
        CreditLimitHistoryBase(
            credit_limit=Decimal("5000.123"), effective_date=now  # 3 decimal places
        )

    # Test valid precision at the boundary
    data = CreditLimitHistoryBase(
        credit_limit=Decimal("5000.12"), effective_date=now  # 2 decimal places
    )
    assert data.credit_limit == Decimal("5000.12")


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CreditLimitHistoryBase(
            credit_limit=Decimal("5000.00"),
            effective_date=datetime.now(),  # Naive datetime
        )

    # Test non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CreditLimitHistoryBase(
            credit_limit=Decimal("5000.00"),
            effective_date=datetime.now(
                ZoneInfo("America/New_York")
            ),  # Non-UTC timezone
        )

    # Test multiple UTC datetime fields
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CreditLimitHistoryInDB(
            id=1,
            account_id=2,
            credit_limit=Decimal("5000.00"),
            effective_date=datetime.now(timezone.utc),
            created_at=datetime.now(),  # Naive datetime
        )

    # Test valid UTC datetime
    now = datetime.now(timezone.utc)
    data = CreditLimitHistoryBase(credit_limit=Decimal("5000.00"), effective_date=now)
    assert data.effective_date == now
