"""
Unit tests for PaymentAppAccount schemas.

Tests the payment app account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
)
from src.utils.datetime_utils import utc_now


def test_payment_app_account_create_schema():
    """Test the payment app account create schema."""
    # Test with minimum required fields
    payment_app = PaymentAppAccountCreate(
        name="Basic Payment App",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Venmo",
    )
    assert payment_app.name == "Basic Payment App"
    assert payment_app.account_type == "payment_app"
    assert payment_app.current_balance == Decimal("200.00")
    assert payment_app.platform == "Venmo"

    # Test with all fields
    payment_app = PaymentAppAccountCreate(
        name="Full Payment App",
        account_type="payment_app",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        institution="PayPal Holdings, Inc.",
        currency="USD",
        account_number="PP-12345678",
        platform="PayPal",
        has_debit_card=True,
        card_last_four="5678",
        linked_account_ids="1,2,3",
        supports_direct_deposit=True,
        supports_crypto=True,
    )
    assert payment_app.platform == "PayPal"
    assert payment_app.has_debit_card is True
    assert payment_app.card_last_four == "5678"
    assert payment_app.linked_account_ids == "1,2,3"
    assert payment_app.supports_direct_deposit is True
    assert payment_app.supports_crypto is True

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'payment_app'"):
        PaymentAppAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="Venmo",
        )

    # Test validation of payment app-specific field
    with pytest.raises(ValidationError, match="platform"):
        PaymentAppAccountCreate(
            name="Invalid Platform",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            # Missing required platform
        )


def test_payment_app_account_response_schema():
    """Test the payment app account response schema."""
    now = utc_now()

    # Test with minimum required fields
    payment_app_response = PaymentAppAccountResponse(
        id=1,
        name="Payment App Response",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Venmo",
        created_at=now,
        updated_at=now,
    )
    assert payment_app_response.id == 1
    assert payment_app_response.name == "Payment App Response"
    assert payment_app_response.account_type == "payment_app"
    assert payment_app_response.current_balance == Decimal("200.00")
    assert payment_app_response.platform == "Venmo"
    assert payment_app_response.created_at == now
    assert payment_app_response.updated_at == now

    # Test with all fields
    payment_app_response = PaymentAppAccountResponse(
        id=2,
        name="Full Payment App",
        account_type="payment_app",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        institution="PayPal Holdings, Inc.",
        currency="USD",
        account_number="PP-12345678",
        platform="PayPal",
        has_debit_card=True,
        card_last_four="5678",
        linked_account_ids="1,2,3",
        supports_direct_deposit=True,
        supports_crypto=True,
        created_at=now,
        updated_at=now,
    )
    assert payment_app_response.platform == "PayPal"
    assert payment_app_response.has_debit_card is True
    assert payment_app_response.card_last_four == "5678"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'payment_app'"):
        PaymentAppAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="Venmo",
            created_at=now,
            updated_at=now,
        )


def test_payment_app_platform_validation():
    """Test platform validation in payment app account schemas."""
    # Test various valid platforms
    valid_platforms = [
        "PayPal",
        "Venmo",
        "Cash App",
        "Zelle",
        "Apple Pay",
        "Google Pay",
    ]

    for platform in valid_platforms:
        payment_app = PaymentAppAccountCreate(
            name="Platform Test",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform=platform,
        )
        assert payment_app.platform == platform

    # Test invalid platform
    with pytest.raises(ValidationError, match="Platform must be one of:"):
        payment_app = PaymentAppAccountCreate(
            name="Invalid Platform",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="Other Payment Service",  # Not in the allowed values
        )


def test_card_last_four_validation():
    """Test card last four validation in payment app account schemas."""
    # Test valid card last four with debit card
    payment_app = PaymentAppAccountCreate(
        name="Card Test",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        has_debit_card=True,
        card_last_four="1234",
    )
    assert payment_app.has_debit_card is True
    assert payment_app.card_last_four == "1234"

    # Test no card last four with no debit card
    payment_app = PaymentAppAccountCreate(
        name="No Card Test",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Venmo",
        has_debit_card=False,
    )
    assert payment_app.has_debit_card is False
    assert payment_app.card_last_four is None

    # Test invalid card last four (non-numeric characters)
    with pytest.raises(
        ValidationError, match="Card last four digits must contain only numbers"
    ):
        PaymentAppAccountCreate(
            name="Invalid Card",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="abcd",  # Should be numeric
        )

    # Test invalid card last four (wrong length)
    with pytest.raises(
        ValidationError, match="String should have at most 4 characters"
    ):
        PaymentAppAccountCreate(
            name="Invalid Card Length",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="12345",  # Should be 4 digits
        )
