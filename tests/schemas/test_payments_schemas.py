from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.payments import (
    PaymentBase,
    PaymentCreate,
    PaymentDateRange,
    PaymentSourceBase,
    PaymentSourceCreate,
    PaymentUpdate,
)


def test_payment_source_base_validation():
    """Test PaymentSourceBase validation rules."""
    # Valid data
    valid_data = {"account_id": 1, "amount": Decimal("100.00")}
    source = PaymentSourceBase(**valid_data)
    assert source.account_id == 1
    assert source.amount == Decimal("100.00")

    # Invalid account_id
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentSourceBase(account_id=0, amount=Decimal("100.00"))

    # Invalid amount (negative)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentSourceBase(account_id=1, amount=Decimal("-100.00"))

    # Invalid amount (too many decimal places)
    with pytest.raises(
        ValidationError, match="Amount must have at most 2 decimal places"
    ):
        PaymentSourceBase(account_id=1, amount=Decimal("100.001"))


def test_payment_base_validation():
    """Test PaymentBase validation rules."""
    now = datetime.now(timezone.utc)

    # Valid data
    valid_data = {
        "amount": Decimal("100.00"),
        "payment_date": now,
        "description": "Test payment",
        "category": "Test category",
    }
    payment = PaymentBase(**valid_data)
    assert payment.amount == Decimal("100.00")
    assert payment.payment_date == now
    assert payment.description == "Test payment"
    assert payment.category == "Test category"

    # Invalid amount (negative)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentBase(**{**valid_data, "amount": Decimal("-100.00")})

    # Invalid amount (too many decimal places)
    with pytest.raises(
        ValidationError, match="Amount must have at most 2 decimal places"
    ):
        PaymentBase(**{**valid_data, "amount": Decimal("100.001")})

    # Invalid payment_date (future)
    with pytest.raises(ValidationError, match="Payment date cannot be in the future"):
        PaymentBase(**{**valid_data, "payment_date": now + timedelta(days=1)})

    # Invalid payment_date (naive datetime)
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentBase(**{**valid_data, "payment_date": datetime.now()})

    # Invalid description (empty string)
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        PaymentBase(**{**valid_data, "description": ""})

    # Invalid description (too long)
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        PaymentBase(**{**valid_data, "description": "a" * 501})

    # Invalid category (empty string)
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        PaymentBase(**{**valid_data, "category": ""})

    # Invalid category (too long)
    with pytest.raises(
        ValidationError, match="String should have at most 100 characters"
    ):
        PaymentBase(**{**valid_data, "category": "a" * 101})


def test_payment_create_validation():
    """Test PaymentCreate validation rules."""
    now = datetime.now(timezone.utc)

    # Valid data
    valid_data = {
        "amount": Decimal("100.00"),
        "payment_date": now,
        "description": "Test payment",
        "category": "Test category",
        "liability_id": 1,
        "sources": [
            {"account_id": 1, "amount": Decimal("60.00")},
            {"account_id": 2, "amount": Decimal("40.00")},
        ],
    }
    payment = PaymentCreate(**valid_data)
    assert payment.amount == Decimal("100.00")
    assert len(payment.sources) == 2

    # Invalid: no sources
    with pytest.raises(
        ValidationError, match="At least one payment source is required"
    ):
        PaymentCreate(**{**valid_data, "sources": []})

    # Invalid: sources total doesn't match amount
    invalid_sources = [
        {"account_id": 1, "amount": Decimal("60.00")},
        {"account_id": 2, "amount": Decimal("30.00")},
    ]
    with pytest.raises(
        ValidationError, match="Sum of payment sources .* must equal payment amount"
    ):
        PaymentCreate(**{**valid_data, "sources": invalid_sources})

    # Invalid: duplicate account IDs
    duplicate_sources = [
        {"account_id": 1, "amount": Decimal("60.00")},
        {"account_id": 1, "amount": Decimal("40.00")},
    ]
    with pytest.raises(
        ValidationError, match="Duplicate account IDs in payment sources"
    ):
        PaymentCreate(**{**valid_data, "sources": duplicate_sources})


def test_payment_update_validation():
    """Test PaymentUpdate validation rules."""
    now = datetime.now(timezone.utc)

    # Valid data (partial update)
    valid_data = {
        "amount": Decimal("100.00"),
        "sources": [{"account_id": 1, "amount": Decimal("100.00")}],
    }
    payment = PaymentUpdate(**valid_data)
    assert payment.amount == Decimal("100.00")
    assert len(payment.sources) == 1

    # Valid data (no sources update)
    valid_no_sources = {
        "amount": Decimal("100.00"),
        "description": "Updated description",
    }
    payment = PaymentUpdate(**valid_no_sources)
    assert payment.amount == Decimal("100.00")
    assert payment.sources is None

    # Invalid: empty sources list
    with pytest.raises(
        ValidationError, match="At least one payment source is required"
    ):
        PaymentUpdate(**{**valid_data, "sources": []})

    # Invalid: sources total doesn't match amount
    invalid_sources = [{"account_id": 1, "amount": Decimal("90.00")}]
    with pytest.raises(
        ValidationError, match="Sum of payment sources .* must equal payment amount"
    ):
        PaymentUpdate(**{**valid_data, "sources": invalid_sources})

    # Invalid: duplicate account IDs
    duplicate_sources = [
        {"account_id": 1, "amount": Decimal("50.00")},
        {"account_id": 1, "amount": Decimal("50.00")},
    ]
    with pytest.raises(
        ValidationError, match="Duplicate account IDs in payment sources"
    ):
        PaymentUpdate(**{**valid_data, "sources": duplicate_sources})


def test_payment_date_range_validation():
    """Test PaymentDateRange validation rules."""
    now = datetime.now(timezone.utc)

    # Valid date range
    valid_data = {"start_date": now - timedelta(days=1), "end_date": now}
    date_range = PaymentDateRange(**valid_data)
    assert date_range.start_date == valid_data["start_date"]
    assert date_range.end_date == valid_data["end_date"]

    # Invalid: end_date before start_date
    invalid_data = {"start_date": now, "end_date": now - timedelta(days=1)}
    with pytest.raises(ValidationError, match="End date must be after start date"):
        PaymentDateRange(**invalid_data)

    # Invalid: naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentDateRange(
            start_date=datetime.now(), end_date=datetime.now() + timedelta(days=1)
        )
