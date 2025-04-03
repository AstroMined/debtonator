"""
Unit tests for EWAAccount schemas.

Tests the Earned Wage Access (EWA) account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.ewa import EWAAccountCreate, EWAAccountResponse
from src.utils.datetime_utils import utc_now


def test_ewa_account_create_schema():
    """Test the EWA account create schema."""
    # Test with minimum required fields
    ewa = EWAAccountCreate(
        name="Basic EWA",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
    )
    assert ewa.name == "Basic EWA"
    assert ewa.account_type == "ewa"
    assert ewa.provider == "DailyPay"

    # Test with all fields including dates
    period_start = utc_now()
    period_end = utc_now()
    payday = utc_now()

    ewa = EWAAccountCreate(
        name="Full EWA",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="DailyPay, Inc.",
        currency="USD",
        account_number="EWA-12345",
        provider="DailyPay",
        max_advance_percentage=Decimal("0.50"),  # 50%
        per_transaction_fee=Decimal("2.99"),
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
    )
    assert ewa.provider == "DailyPay"
    assert ewa.max_advance_percentage == Decimal("0.50")
    assert ewa.per_transaction_fee == Decimal("2.99")
    assert ewa.pay_period_start == period_start
    assert ewa.pay_period_end == period_end
    assert ewa.next_payday == payday

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        EWAAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="DailyPay",
        )

    # Test validation of EWA-specific field
    with pytest.raises(ValidationError, match="provider"):
        EWAAccountCreate(
            name="Invalid Provider",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            # Missing required provider
        )


def test_ewa_account_response_schema():
    """Test the EWA account response schema."""
    now = utc_now()

    # Test with minimum required fields
    ewa_response = EWAAccountResponse(
        id=1,
        name="EWA Response",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
        created_at=now,
        updated_at=now,
    )
    assert ewa_response.id == 1
    assert ewa_response.name == "EWA Response"
    assert ewa_response.account_type == "ewa"
    assert ewa_response.provider == "DailyPay"
    assert ewa_response.created_at == now
    assert ewa_response.updated_at == now

    # Test with all fields
    ewa_response = EWAAccountResponse(
        id=2,
        name="Full EWA Response",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="DailyPay, Inc.",
        currency="USD",
        account_number="EWA-12345",
        provider="DailyPay",
        max_advance_percentage=Decimal("0.50"),  # 50%
        per_transaction_fee=Decimal("2.99"),
        pay_period_start=now,
        pay_period_end=now,
        next_payday=now,
        created_at=now,
        updated_at=now,
    )
    assert ewa_response.provider == "DailyPay"
    assert ewa_response.max_advance_percentage == Decimal("0.50")
    assert ewa_response.per_transaction_fee == Decimal("2.99")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        EWAAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="DailyPay",
            created_at=now,
            updated_at=now,
        )


def test_ewa_provider_validation():
    """Test EWA provider validation in EWA account schemas."""
    # Test various valid providers (this list should be updated if the actual validation changes)
    valid_providers = ["DailyPay", "Even", "PayActiv", "Branch", "FlexWage"]

    for provider in valid_providers:
        ewa = EWAAccountCreate(
            name="Provider Test",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider=provider,
        )
        assert ewa.provider == provider

    # Test custom/other provider
    ewa = EWAAccountCreate(
        name="Custom Provider",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Other EWA Provider",  # Custom provider name
    )
    assert ewa.provider == "Other EWA Provider"


def test_ewa_max_advance_validation():
    """Test max advance percentage validation in EWA account schemas."""
    # Test valid max advance percentage
    ewa = EWAAccountCreate(
        name="Valid Advance",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
        max_advance_percentage=Decimal("0.80"),  # 80%
    )
    assert ewa.max_advance_percentage == Decimal("0.80")

    # Test negative max advance
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        EWAAccountCreate(
            name="Invalid Advance",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="DailyPay",
            max_advance_percentage=Decimal("-0.10"),  # Negative value not allowed
        )

    # Test max advance > 100%
    with pytest.raises(ValidationError, match="less than or equal to 1"):
        EWAAccountCreate(
            name="Invalid Advance",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="DailyPay",
            max_advance_percentage=Decimal("1.20"),  # Can't advance more than 100%
        )


def test_ewa_pay_period_validation():
    """Test pay period validation in EWA account schemas."""
    now = utc_now()
    future = utc_now()  # Normally would add time, but this is fine for schema testing

    # Test with all pay period fields
    ewa = EWAAccountCreate(
        name="Period Test",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
        pay_period_start=now,
        pay_period_end=future,
        next_payday=future,
    )
    assert ewa.pay_period_start == now
    assert ewa.pay_period_end == future
    assert ewa.next_payday == future

    # Test with missing pay_period_end
    ewa = EWAAccountCreate(
        name="Missing End",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
        pay_period_start=now,
        # Missing pay_period_end
        next_payday=future,
    )
    assert ewa.pay_period_start == now
    assert ewa.pay_period_end is None
    assert ewa.next_payday == future
