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
        platform="PayPal",
    )
    assert payment_app.name == "Basic Payment App"
    assert payment_app.account_type == "payment_app"
    assert payment_app.platform == "PayPal"

    # Test with all fields
    payment_app = PaymentAppAccountCreate(
        name="Full Payment App",
        account_type="payment_app",
        current_balance=Decimal("350.00"),
        available_balance=Decimal("350.00"),
        institution="PayPal, Inc.",
        currency="USD",
        account_number="user@example.com",
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
    with pytest.raises(ValidationError, match="Value error at account_type"):
        PaymentAppAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
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
        platform="PayPal",
        created_at=now,
        updated_at=now,
    )
    assert payment_app_response.id == 1
    assert payment_app_response.name == "Payment App Response"
    assert payment_app_response.account_type == "payment_app"
    assert payment_app_response.platform == "PayPal"
    assert payment_app_response.created_at == now
    assert payment_app_response.updated_at == now

    # Test with all fields
    payment_app_response = PaymentAppAccountResponse(
        id=2,
        name="Full Payment App",
        account_type="payment_app",
        current_balance=Decimal("350.00"),
        available_balance=Decimal("350.00"),
        institution="PayPal, Inc.",
        currency="USD",
        account_number="user@example.com",
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
    assert payment_app_response.linked_account_ids == "1,2,3"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        PaymentAppAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            created_at=now,
            updated_at=now,
        )


def test_payment_app_platform_validation():
    """Test platform validation in payment app schemas."""
    # Test various valid platforms (this list should be updated if the actual validation changes)
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

    # Test custom/other platform
    payment_app = PaymentAppAccountCreate(
        name="Custom Platform",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Other Payment Service",  # Custom platform name
    )
    assert payment_app.platform == "Other Payment Service"


def test_card_last_four_validation():
    """Test card_last_four validation in payment app schemas."""
    # Test valid last four digits
    payment_app = PaymentAppAccountCreate(
        name="Card Test",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        has_debit_card=True,
        card_last_four="1234",
    )
    assert payment_app.card_last_four == "1234"

    # Test invalid (too short) last four
    with pytest.raises(
        ValidationError, match="String should have at least 4 characters"
    ):
        PaymentAppAccountCreate(
            name="Invalid Card",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="123",  # Too short
        )

    # Test invalid (too long) last four
    with pytest.raises(
        ValidationError, match="String should have at most 4 characters"
    ):
        PaymentAppAccountCreate(
            name="Invalid Card",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="12345",  # Too long
        )

    # Test invalid (non-numeric) last four
    with pytest.raises(ValidationError, match="String should match pattern"):
        PaymentAppAccountCreate(
            name="Invalid Card",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="abcd",  # Non-numeric
        )
