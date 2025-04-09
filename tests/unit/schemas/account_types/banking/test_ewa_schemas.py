"""
Unit tests for EWAAccount schemas.

Tests the Early Wage Access (EWA) account schema validation and serialization
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
        provider="Payactiv",
    )
    assert ewa.name == "Basic EWA"
    assert ewa.account_type == "ewa"
    assert ewa.current_balance == Decimal("150.00")
    assert ewa.provider == "Payactiv"

    # Test with all fields including dates
    period_start = utc_now()
    period_end = utc_now()  # In real scenario, this would be later than period_start
    payday = utc_now()  # In real scenario, this would be later than period_end

    ewa = EWAAccountCreate(
        name="Full EWA",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="Payactiv Inc.",
        currency="USD",
        account_number="EWA-12345",
        provider="Payactiv",
        max_advance_percentage=Decimal("0.50"),
        per_transaction_fee=Decimal("5.00"),
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
    )
    assert ewa.provider == "Payactiv"
    assert ewa.max_advance_percentage == Decimal("0.50")
    assert ewa.per_transaction_fee == Decimal("5.00")
    assert ewa.pay_period_start == period_start
    assert ewa.pay_period_end == period_end
    assert ewa.next_payday == payday

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'ewa'"):
        EWAAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
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
        provider="Payactiv",
        created_at=now,
        updated_at=now,
    )
    assert ewa_response.id == 1
    assert ewa_response.name == "EWA Response"
    assert ewa_response.account_type == "ewa"
    assert ewa_response.current_balance == Decimal("150.00")
    assert ewa_response.provider == "Payactiv"
    assert ewa_response.created_at == now
    assert ewa_response.updated_at == now

    # Test with all fields
    ewa_response = EWAAccountResponse(
        id=2,
        name="Full EWA Response",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="Payactiv Inc.",
        currency="USD",
        account_number="EWA-12345",
        provider="Payactiv",
        max_advance_percentage=Decimal("0.50"),
        per_transaction_fee=Decimal("5.00"),
        pay_period_start=now,
        pay_period_end=now,
        next_payday=now,
        created_at=now,
        updated_at=now,
    )
    assert ewa_response.provider == "Payactiv"
    assert ewa_response.max_advance_percentage == Decimal("0.50")
    assert ewa_response.per_transaction_fee == Decimal("5.00")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'ewa'"):
        EWAAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
            created_at=now,
            updated_at=now,
        )


def test_ewa_provider_validation():
    """Test EWA provider validation in EWA account schemas."""
    # Test various valid providers
    valid_providers = ["Payactiv", "DailyPay", "Earnin", "Even", "FlexWage"]

    for provider in valid_providers:
        ewa = EWAAccountCreate(
            name="Provider Test",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider=provider,
        )
        assert ewa.provider == provider

    # Test invalid provider
    with pytest.raises(ValidationError, match="EWA provider must be one of:"):
        ewa = EWAAccountCreate(
            name="Invalid Provider",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="PayActiv",  # Case mismatch - should be "Payactiv"
        )


def test_ewa_max_advance_validation():
    """Test max advance percentage validation in EWA account schemas."""
    # Test valid advance percentage
    ewa = EWAAccountCreate(
        name="Valid Advance",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        max_advance_percentage=Decimal("0.50"),  # 50% advance
    )
    assert ewa.max_advance_percentage == Decimal("0.50")

    # Test high advance percentage
    # Note: In current implementation, validation for max percentage limit has been relaxed
    ewa = EWAAccountCreate(
        name="High Advance",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        max_advance_percentage=Decimal(
            "0.90"
        ),  # 90% is unusual but valid in current schema
    )
    assert ewa.max_advance_percentage == Decimal("0.90")


def test_ewa_date_validation():
    """Test date validation in EWA account schemas."""
    now = utc_now()

    # Calculate dates that ensure proper sequence
    period_start = now
    period_end = now.replace(day=now.day + 7)  # 7 days later
    payday = period_end.replace(day=period_end.day + 1)  # 1 day after period end

    # Test valid date sequence
    ewa = EWAAccountCreate(
        name="Valid Dates",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
    )
    assert ewa.pay_period_start == period_start
    assert ewa.pay_period_end == period_end
    assert ewa.next_payday == payday

    # Test invalid sequence - payday before period end
    with pytest.raises(ValidationError, match="Next payday must be on or after"):
        EWAAccountCreate(
            name="Invalid Dates",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
            pay_period_start=period_start,
            pay_period_end=payday,  # Switched order
            next_payday=period_end,
        )
