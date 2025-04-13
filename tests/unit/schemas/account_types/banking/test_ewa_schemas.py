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
    EWAAccountResponse,
    EWAAccountUpdate,
)
from src.utils.datetime_utils import days_from_now, utc_datetime, utc_now


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
    payday = days_from_now(15)  # a day after period_end

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
        "Payactiv",
        "DailyPay",
        "Earnin",
        "Even",
        "FlexWage",
        "Branch",
        "Instant",
        "Rain",
        "Other",
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
    past = days_from_now(-1)  # 1 day in the past

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
    with pytest.raises(
        ValidationError, match="Pay period end date must be after start date"
    ):
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
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        EWAAccountCreate(
            name="Negative Fee",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="Payactiv",
            per_transaction_fee=Decimal("-1.00"),
        )


def test_ewa_account_base_instantiation():
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


def test_ewa_account_update_schema():
    """Test the EWA account update schema."""
    # Test empty update (all fields optional)
    update = EWAAccountUpdate()
    assert update.name is None
    assert update.account_type is None
    assert update.current_balance is None
    assert update.available_balance is None
    assert update.provider is None
    assert update.max_advance_percentage is None
    assert update.per_transaction_fee is None
    assert update.pay_period_start is None
    assert update.pay_period_end is None
    assert update.next_payday is None

    # Test partial update
    update = EWAAccountUpdate(
        name="Updated EWA",
        provider="DailyPay",
    )
    assert update.name == "Updated EWA"
    assert update.provider == "DailyPay"
    assert update.account_type is None  # Not updated
    assert update.current_balance is None  # Not updated

    # Test full update
    now = utc_now()
    future = days_from_now(14)
    payday = days_from_now(15)

    update = EWAAccountUpdate(
        name="Fully Updated EWA",
        account_type="ewa",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        provider="Earnin",
        max_advance_percentage=Decimal("0.60"),
        per_transaction_fee=Decimal("3.99"),
        pay_period_start=now,
        pay_period_end=future,
        next_payday=payday,
    )
    assert update.name == "Fully Updated EWA"
    assert update.account_type == "ewa"
    assert update.current_balance == Decimal("300.00")
    assert update.available_balance == Decimal("300.00")
    assert update.provider == "Earnin"
    assert update.max_advance_percentage == Decimal("0.60")
    assert update.per_transaction_fee == Decimal("3.99")
    assert update.pay_period_start == now
    assert update.pay_period_end == future
    assert update.next_payday == payday

    # Test invalid account type in update
    with pytest.raises(ValidationError, match="Input should be 'ewa'"):
        EWAAccountUpdate(
            account_type="checking",  # Wrong type
        )


def test_update_provider_validation():
    """Test provider validation in EWA account update schema."""
    # Test valid provider update
    update = EWAAccountUpdate(
        provider="Branch",  # Valid provider
    )
    assert update.provider == "Branch"

    # Test invalid provider update
    with pytest.raises(ValidationError, match="EWA provider must be one of:"):
        EWAAccountUpdate(
            provider="Invalid Provider",  # Not in allowed values
        )

    # Test None provider (no update)
    update = EWAAccountUpdate(
        provider=None,
    )
    assert update.provider is None


def test_update_max_advance_percentage():
    """Test max advance percentage validation in EWA account update schema."""
    # Test valid update
    update = EWAAccountUpdate(
        max_advance_percentage=Decimal("0.75"),
    )
    assert update.max_advance_percentage == Decimal("0.75")

    # Test high percentage (now allowed)
    update = EWAAccountUpdate(
        max_advance_percentage=Decimal("0.95"),
    )
    assert update.max_advance_percentage == Decimal("0.95")

    # Test percentage at upper limit
    update = EWAAccountUpdate(
        max_advance_percentage=Decimal("1.00"),
    )
    assert update.max_advance_percentage == Decimal("1.00")

    # Test None value (no update)
    update = EWAAccountUpdate(
        max_advance_percentage=None,
    )
    assert update.max_advance_percentage is None


def test_update_per_transaction_fee():
    """Test per transaction fee validation in EWA account update schema."""
    # Test valid update
    update = EWAAccountUpdate(
        per_transaction_fee=Decimal("4.50"),
    )
    assert update.per_transaction_fee == Decimal("4.50")

    # Test zero fee
    update = EWAAccountUpdate(
        per_transaction_fee=Decimal("0.00"),
    )
    assert update.per_transaction_fee == Decimal("0.00")

    # Test negative fee (invalid)
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        EWAAccountUpdate(
            per_transaction_fee=Decimal("-1.00"),
        )

    # Test None value (no update)
    update = EWAAccountUpdate(
        per_transaction_fee=None,
    )
    assert update.per_transaction_fee is None


def test_update_pay_period_dates():
    """Test pay period date validations in EWA account update schema."""
    now = utc_now()
    future = days_from_now(14)
    past = days_from_now(-1)

    # Test valid update with both dates
    update = EWAAccountUpdate(
        pay_period_start=now,
        pay_period_end=future,
    )
    assert update.pay_period_start == now
    assert update.pay_period_end == future

    # Test invalid dates (end before start)
    with pytest.raises(
        ValidationError, match="Pay period end date must be after start date"
    ):
        EWAAccountUpdate(
            pay_period_start=now,
            pay_period_end=past,
        )

    # Test update with only start date
    update = EWAAccountUpdate(
        pay_period_start=now,
    )
    assert update.pay_period_start == now
    assert update.pay_period_end is None

    # Test update with only end date
    update = EWAAccountUpdate(
        pay_period_end=future,
    )
    assert update.pay_period_start is None
    assert update.pay_period_end == future

    # Test None values (no update)
    update = EWAAccountUpdate(
        pay_period_start=None,
        pay_period_end=None,
    )
    assert update.pay_period_start is None
    assert update.pay_period_end is None


def test_update_next_payday():
    """Test next payday validation in EWA account update schema."""
    now = utc_now()
    specific_date = utc_datetime(2025, 5, 15, 12, 0, 0)

    # Test valid update
    update = EWAAccountUpdate(
        next_payday=now,
    )
    assert update.next_payday == now
    assert update.next_payday.tzinfo is not None  # Should have timezone info

    # Test with specific date
    update = EWAAccountUpdate(
        next_payday=specific_date,
    )
    assert update.next_payday == specific_date
    assert update.next_payday.tzinfo is not None  # Should have timezone info

    # Test None value (no update)
    update = EWAAccountUpdate(
        next_payday=None,
    )
    assert update.next_payday is None


def test_complex_pay_period_scenarios():
    """Test complex scenarios with pay period dates."""
    # Test updating pay period start to be after existing end date
    # This should be valid since we're only validating when both are provided together
    now = utc_now()
    future1 = days_from_now(7)
    future2 = days_from_now(14)

    # First create an account with initial dates
    ewa = EWAAccountCreate(
        name="Pay Period Test",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="Payactiv",
        pay_period_start=now,
        pay_period_end=future1,
    )
    assert ewa.pay_period_start == now
    assert ewa.pay_period_end == future1

    # Now update only the start date to be after the end date
    # In a real application, this would be validated at the service layer
    # The schema only validates when both are provided in the same update
    update = EWAAccountUpdate(
        pay_period_start=future2,  # After the existing end date
    )
    assert update.pay_period_start == future2
    assert update.pay_period_end is None

    # Test updating both dates to valid values
    update = EWAAccountUpdate(
        pay_period_start=future1,
        pay_period_end=future2,
    )
    assert update.pay_period_start == future1
    assert update.pay_period_end == future2


def test_next_payday_normalization_in_update():
    """Test next payday normalization in EWA account update schema."""
    # Create datetime objects using utility functions
    now = utc_now()
    specific_date = utc_datetime(2025, 6, 15, 12, 0, 0)

    # Test with standard UTC datetime
    update = EWAAccountUpdate(
        next_payday=now,
    )
    assert update.next_payday.tzinfo is not None  # Should have timezone info
    assert update.next_payday == now  # Should remain as is

    # Test with specific UTC datetime
    update = EWAAccountUpdate(
        next_payday=specific_date,
    )
    assert update.next_payday.tzinfo is not None  # Should have timezone info
    assert update.next_payday == specific_date  # Should remain as is
