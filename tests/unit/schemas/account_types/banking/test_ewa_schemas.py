"""
Unit tests for EWAAccount schemas.

Tests the Early Wage Access (EWA) account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.ewa import (
    EWAAccountBase,
    EWAAccountCreate,
    EWAAccountResponse
)
from src.utils.datetime_utils import (
    utc_now, 
    days_from_now,
    utc_datetime
)


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
    period_end = days_from_now(14)  # 2 weeks after period_start
    payday = days_from_now(15)      # a day after period_end

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
        pay_period_end=days_from_now(14),
        next_payday=days_from_now(15),
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
    valid_providers = [
        "Payactiv", "DailyPay", "Earnin", "Even", "FlexWage", 
        "Branch", "Instant", "Rain", "Other"
    ]

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

    # Test another invalid provider
    with pytest.raises(ValidationError, match="EWA provider must be one of:"):
        ewa = EWAAccountCreate(
            name="Invalid Provider",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Unknown Provider",  # Not in the list of valid providers
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

    # Test high advance percentage - now allowed since reasonableness validation moved to service layer
    # This previously raised an error when we had the validator in the schema
    ewa = EWAAccountCreate(
        name="High Advance",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        max_advance_percentage=Decimal("0.85"),  # 85% - now allowed
    )
    assert ewa.max_advance_percentage == Decimal("0.85")

    # Test advance percentage at 100% - also now allowed
    ewa = EWAAccountCreate(
        name="Full Advance",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        max_advance_percentage=Decimal("1.00"),  # 100% - now allowed
    )
    assert ewa.max_advance_percentage == Decimal("1.00")


def test_ewa_pay_period_dates_validation():
    """Test pay period date validations in EWA account schemas."""
    now = utc_now()
    future = days_from_now(14)  # 14 days in the future
    past = days_from_now(-1)    # 1 day in the past

    # Test valid dates (period_end after period_start)
    ewa = EWAAccountCreate(
        name="Valid Pay Period",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        pay_period_start=now,
        pay_period_end=future,  # 14 days after start
    )
    assert ewa.pay_period_start == now
    assert ewa.pay_period_end == future

    # Test invalid dates (period_end before period_start)
    with pytest.raises(ValidationError, match="Pay period end date must be after start date"):
        EWAAccountCreate(
            name="Invalid Pay Period",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
            pay_period_start=now,
            pay_period_end=past,  # 1 day before now
        )

    # Test with only period_start
    ewa = EWAAccountCreate(
        name="Partial Pay Period",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        pay_period_start=now,
        # No pay_period_end provided
    )
    assert ewa.pay_period_start == now
    assert ewa.pay_period_end is None

    # Test with only period_end
    ewa = EWAAccountCreate(
        name="Partial Pay Period",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        # No pay_period_start provided
        pay_period_end=now,
    )
    assert ewa.pay_period_start is None
    assert ewa.pay_period_end == now


def test_ewa_next_payday_normalization():
    """Test next payday date normalization in EWA account schemas."""
    # Create datetime objects using utility functions
    now = utc_now()
    specific_date = utc_datetime(2025, 4, 15, 12, 0, 0)
    
    # Test with standard UTC datetime
    ewa = EWAAccountCreate(
        name="UTC Datetime Test",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        next_payday=now,
    )
    assert ewa.next_payday.tzinfo is not None  # Should have timezone info
    assert ewa.next_payday == now  # Should remain as is
    
    # Test with specific UTC datetime
    ewa = EWAAccountCreate(
        name="Specific UTC Datetime Test",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        next_payday=specific_date,
    )
    assert ewa.next_payday.tzinfo is not None  # Should have timezone info
    assert ewa.next_payday == specific_date  # Should remain as is


def test_ewa_transaction_fee_validation():
    """Test transaction fee validation in EWA account schemas."""
    # Test valid transaction fee
    ewa = EWAAccountCreate(
        name="Valid Fee",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        per_transaction_fee=Decimal("5.99"),
    )
    assert ewa.per_transaction_fee == Decimal("5.99")

    # Test zero transaction fee
    ewa = EWAAccountCreate(
        name="Zero Fee",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        per_transaction_fee=Decimal("0.00"),
    )
    assert ewa.per_transaction_fee == Decimal("0.00")

    # Test negative transaction fee (should raise validation error)
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        EWAAccountCreate(
            name="Negative Fee",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
            per_transaction_fee=Decimal("-1.00"),
        )


def test_ewa_account_base_inheritance():
    """Test that EWAAccountBase can be instantiated directly."""
    # Test with minimum required fields
    ewa_base = EWAAccountBase(
        name="Base EWA",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
    )
    assert ewa_base.name == "Base EWA"
    assert ewa_base.account_type == "ewa"
    assert ewa_base.provider == "Payactiv"
    
    # Test with additional fields
    ewa_base = EWAAccountBase(
        name="Full Base EWA",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        provider="DailyPay",
        max_advance_percentage=Decimal("0.40"),
        per_transaction_fee=Decimal("4.99"),
    )
    assert ewa_base.provider == "DailyPay"
    assert ewa_base.max_advance_percentage == Decimal("0.40")
    assert ewa_base.per_transaction_fee == Decimal("4.99")
