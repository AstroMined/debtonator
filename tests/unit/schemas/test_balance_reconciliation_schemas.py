from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.balance_reconciliation import (
    BalanceReconciliation,
    BalanceReconciliationBase,
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.utils.datetime_utils import utc_datetime, utc_now


# Test valid object creation
def test_balance_reconciliation_base_valid():
    """Test valid balance reconciliation base schema"""
    data = BalanceReconciliationBase(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        reason="Monthly reconciliation",
    )

    assert data.account_id == 1
    assert data.previous_balance == Decimal("1000.00")
    assert data.new_balance == Decimal("1200.00")
    assert data.reason == "Monthly reconciliation"


def test_balance_reconciliation_base_minimal():
    """Test balance reconciliation base with only required fields"""
    data = BalanceReconciliationBase(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
    )

    assert data.account_id == 1
    assert data.previous_balance == Decimal("1000.00")
    assert data.new_balance == Decimal("1200.00")
    assert data.reason is None


def test_balance_reconciliation_create_valid():
    """Test valid balance reconciliation create schema"""
    data = BalanceReconciliationCreate(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        adjustment_amount=Decimal("200.00"),  # Add required field
        reason="Monthly reconciliation",
    )

    assert data.account_id == 1
    assert data.previous_balance == Decimal("1000.00")
    assert data.new_balance == Decimal("1200.00")
    assert data.adjustment_amount == Decimal("200.00")  # Verify adjustment_amount
    assert data.reason == "Monthly reconciliation"


def test_adjustment_amount_validator():
    """Test the adjustment_amount validator directly including edge cases."""
    # Create test validator function
    validate_adjustment = BalanceReconciliationCreate.validate_adjustment_amount

    # Test case when values are present and correct
    class MockInfoValid:
        def __init__(self):
            self.data = {
                "new_balance": Decimal("1200.00"),
                "previous_balance": Decimal("1000.00"),
            }

    # Test valid case - adjustment matches difference
    result = validate_adjustment(Decimal("200.00"), MockInfoValid())
    assert result == Decimal("200.00")

    # Test invalid case - adjustment doesn't match difference
    with pytest.raises(
        ValueError, match="adjustment_amount must equal new_balance - previous_balance"
    ):
        validate_adjustment(Decimal("300.00"), MockInfoValid())

    # Test case with missing new_balance (line 50 branch)
    class MockInfoMissingNewBalance:
        def __init__(self):
            self.data = {
                "previous_balance": Decimal("1000.00")
                # new_balance is missing
            }

    # This should pass without validation since new_balance is None
    result = validate_adjustment(Decimal("200.00"), MockInfoMissingNewBalance())
    assert result == Decimal("200.00")

    # Test case with missing previous_balance (line 50 branch)
    class MockInfoMissingPreviousBalance:
        def __init__(self):
            self.data = {
                "new_balance": Decimal("1200.00")
                # previous_balance is missing
            }

    # This should pass without validation since previous_balance is None
    result = validate_adjustment(Decimal("200.00"), MockInfoMissingPreviousBalance())
    assert result == Decimal("200.00")

    # Test case with both values missing (line 50 branch)
    class MockInfoEmpty:
        def __init__(self):
            self.data = {}  # Empty data dict

    # This should pass without validation since both values are None
    result = validate_adjustment(Decimal("200.00"), MockInfoEmpty())
    assert result == Decimal("200.00")


def test_balance_reconciliation_update_valid():
    """Test valid balance reconciliation update schema"""
    data = BalanceReconciliationUpdate(reason="Updated reason")
    assert data.reason == "Updated reason"

    # Empty update should also be valid
    data = BalanceReconciliationUpdate()
    assert data.reason is None


def test_balance_reconciliation_complete_valid():
    """Test valid complete balance reconciliation schema"""
    now = datetime.now(timezone.utc)

    data = BalanceReconciliation(
        id=1,
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        reason="Monthly reconciliation",
        adjustment_amount=Decimal("200.00"),
        reconciliation_date=now,
        created_at=now,
        updated_at=now,
    )

    assert data.id == 1
    assert data.account_id == 1
    assert data.previous_balance == Decimal("1000.00")
    assert data.new_balance == Decimal("1200.00")
    assert data.reason == "Monthly reconciliation"
    assert data.adjustment_amount == Decimal("200.00")
    assert data.reconciliation_date == now
    assert data.created_at == now
    assert data.updated_at == now


# Test field validations
def test_account_id_validation():
    """Test account_id field validation"""
    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        BalanceReconciliationBase(
            previous_balance=Decimal("1000.00"), new_balance=Decimal("1200.00")
        )

    # Test string account_id (type error)
    with pytest.raises(ValidationError, match="Input should be a valid integer"):
        BalanceReconciliationBase(
            account_id="not-an-integer",
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
        )


def test_balances_validation():
    """Test balance fields validation"""
    # Test missing previous_balance
    with pytest.raises(ValidationError, match="Field required"):
        BalanceReconciliationBase(account_id=1, new_balance=Decimal("1200.00"))

    # Test missing new_balance
    with pytest.raises(ValidationError, match="Field required"):
        BalanceReconciliationBase(account_id=1, previous_balance=Decimal("1000.00"))

    # Test non-numeric values
    with pytest.raises(ValidationError, match="Input should be a valid decimal"):
        BalanceReconciliationBase(
            account_id=1,
            previous_balance="not-a-decimal",
            new_balance=Decimal("1200.00"),
        )

    with pytest.raises(ValidationError, match="Input should be a valid decimal"):
        BalanceReconciliationBase(
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance="not-a-decimal",
        )


def test_reason_validation():
    """Test reason field validation"""
    # Test too long reason
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        BalanceReconciliationBase(
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            reason="X" * 501,
        )

    # Test valid long reason (at the limit)
    data = BalanceReconciliationBase(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        reason="X" * 500,
    )
    assert len(data.reason) == 500


# Test decimal precision
def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places in previous_balance
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        BalanceReconciliationBase(
            account_id=1,
            previous_balance=Decimal("1000.123"),
            new_balance=Decimal("1200.00"),
        )

    # Test too many decimal places in new_balance
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        BalanceReconciliationBase(
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.123"),
        )

    # Test too many decimal places in adjustment_amount
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        BalanceReconciliation(
            id=1,
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.123"),
            reconciliation_date=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        BalanceReconciliation(
            id=1,
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.00"),
            reconciliation_date=datetime.now(),  # Naive datetime
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    # Test non-UTC timezone
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        BalanceReconciliation(
            id=1,
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.00"),
            reconciliation_date=datetime.now(
                ZoneInfo("America/New_York")
            ),  # Non-UTC timezone
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    # Test multiple fields with different timezone problems
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        BalanceReconciliation(
            id=1,
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.00"),
            reconciliation_date=datetime.now(timezone.utc),
            created_at=datetime.now(),  # Naive datetime
            updated_at=datetime.now(ZoneInfo("Europe/London")),  # Non-UTC timezone
        )

    # Test with datetime_utils functions
    now = utc_now()
    reconciliation = BalanceReconciliation(
        id=1,
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        adjustment_amount=Decimal("200.00"),
        reconciliation_date=now,
        created_at=now,
        updated_at=now,
    )
    assert reconciliation.reconciliation_date == now

    # Test with specific datetime using utc_datetime
    specific_date = utc_datetime(2025, 3, 15, 14, 30)
    reconciliation = BalanceReconciliation(
        id=1,
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        adjustment_amount=Decimal("200.00"),
        reconciliation_date=specific_date,
        created_at=now,
        updated_at=now,
    )
    assert reconciliation.reconciliation_date == specific_date
    assert reconciliation.reconciliation_date.year == 2025
    assert reconciliation.reconciliation_date.month == 3
    assert reconciliation.reconciliation_date.day == 15


# Test ID validation
def test_id_validation():
    """Test ID field validation in complete schema"""
    now = datetime.now(timezone.utc)

    # Test missing ID
    with pytest.raises(ValidationError, match="Field required"):
        BalanceReconciliation(
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.00"),
            reconciliation_date=now,
            created_at=now,
            updated_at=now,
        )

    # Test non-integer ID
    with pytest.raises(ValidationError, match="Input should be a valid integer"):
        BalanceReconciliation(
            id="not-an-integer",
            account_id=1,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal("1200.00"),
            adjustment_amount=Decimal("200.00"),
            reconciliation_date=now,
            created_at=now,
            updated_at=now,
        )
