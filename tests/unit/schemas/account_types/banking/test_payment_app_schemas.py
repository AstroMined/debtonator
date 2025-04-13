"""
Unit tests for PaymentAppAccount schemas.

Tests the payment app account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountBase,
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
    PaymentAppAccountUpdate,
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


def test_payment_app_account_base_instantiation():
    """Test direct instantiation of PaymentAppAccountBase."""
    # Test with minimum required fields
    payment_app_base = PaymentAppAccountBase(
        name="Base Payment App",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Venmo",
    )
    assert payment_app_base.name == "Base Payment App"
    assert payment_app_base.account_type == "payment_app"
    assert payment_app_base.current_balance == Decimal("200.00")
    assert payment_app_base.platform == "Venmo"
    assert payment_app_base.has_debit_card is False  # Default value
    assert payment_app_base.card_last_four is None  # Default value
    assert payment_app_base.linked_account_ids is None  # Default value
    assert payment_app_base.supports_direct_deposit is False  # Default value
    assert payment_app_base.supports_crypto is False  # Default value

    # Test with all fields
    payment_app_base = PaymentAppAccountBase(
        name="Full Base Payment App",
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
    assert payment_app_base.platform == "PayPal"
    assert payment_app_base.has_debit_card is True
    assert payment_app_base.card_last_four == "5678"
    assert payment_app_base.linked_account_ids == "1,2,3"
    assert payment_app_base.supports_direct_deposit is True
    assert payment_app_base.supports_crypto is True


def test_card_last_four_validation_edge_cases():
    """Test edge cases for card last four validation."""
    # Test card last four with debit card disabled
    with pytest.raises(
        ValidationError,
        match="Card last four digits cannot be provided when debit card is not enabled",
    ):
        PaymentAppAccountCreate(
            name="Invalid Card Config",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=False,
            card_last_four="1234",  # Should not be provided when has_debit_card is False
        )

    # Test missing card last four with debit card enabled
    with pytest.raises(
        ValidationError,
        match="Card last four digits are required when debit card is enabled",
    ):
        PaymentAppAccountCreate(
            name="Missing Card Number",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            # Missing card_last_four
        )

    # Test card last four with minimum length
    with pytest.raises(
        ValidationError, match="String should have at least 4 characters"
    ):
        PaymentAppAccountCreate(
            name="Short Card Number",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            has_debit_card=True,
            card_last_four="123",  # Too short
        )

    # Test card_last_four provided with has_debit_card explicitly set to True
    payment_app = PaymentAppAccountCreate(
        name="Explicit Debit Card",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        has_debit_card=True,  # Explicitly set to True when providing card_last_four
        card_last_four="1234",
    )
    assert payment_app.card_last_four == "1234"
    assert payment_app.has_debit_card is True


def test_linked_account_ids_validation():
    """Test linked account IDs validation in payment app account schemas."""
    # Test valid linked account IDs
    payment_app = PaymentAppAccountCreate(
        name="Linked Accounts Test",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        linked_account_ids="1,2,3",
    )
    assert payment_app.linked_account_ids == "1,2,3"

    # Test linked account IDs with spaces
    payment_app = PaymentAppAccountCreate(
        name="Linked Accounts With Spaces",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        linked_account_ids="1, 2, 3",  # Spaces should be trimmed
    )
    assert payment_app.linked_account_ids == "1,2,3"  # Spaces removed

    # Test invalid linked account IDs (non-numeric)
    with pytest.raises(
        ValidationError,
        match="Linked account IDs must be a comma-separated list of integers",
    ):
        PaymentAppAccountCreate(
            name="Invalid Linked Accounts",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            linked_account_ids="1,two,3",  # Non-numeric value
        )

    # Test invalid linked account IDs (invalid format)
    with pytest.raises(
        ValidationError,
        match="Linked account IDs must be a comma-separated list of integers",
    ):
        PaymentAppAccountCreate(
            name="Invalid Linked Accounts Format",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
            linked_account_ids="1;2;3",  # Wrong separator
        )


def test_payment_app_account_update_schema():
    """Test the payment app account update schema."""
    # Test empty update (all fields optional)
    update = PaymentAppAccountUpdate()
    assert update.name is None
    assert update.account_type is None
    assert update.current_balance is None
    assert update.available_balance is None
    assert update.platform is None
    assert update.has_debit_card is None
    assert update.card_last_four is None
    assert update.linked_account_ids is None
    assert update.supports_direct_deposit is None
    assert update.supports_crypto is None

    # Test partial update
    update = PaymentAppAccountUpdate(
        name="Updated Payment App",
        platform="Cash App",
    )
    assert update.name == "Updated Payment App"
    assert update.platform == "Cash App"
    assert update.account_type is None  # Not updated
    assert update.current_balance is None  # Not updated

    # Test full update
    update = PaymentAppAccountUpdate(
        name="Fully Updated App",
        account_type="payment_app",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        platform="Google Pay",
        has_debit_card=True,
        card_last_four="9876",
        linked_account_ids="4,5,6",
        supports_direct_deposit=True,
        supports_crypto=False,
    )
    assert update.name == "Fully Updated App"
    assert update.account_type == "payment_app"
    assert update.current_balance == Decimal("300.00")
    assert update.available_balance == Decimal("300.00")
    assert update.platform == "Google Pay"
    assert update.has_debit_card is True
    assert update.card_last_four == "9876"
    assert update.linked_account_ids == "4,5,6"
    assert update.supports_direct_deposit is True
    assert update.supports_crypto is False

    # Test invalid account type in update
    with pytest.raises(ValidationError, match="Input should be 'payment_app'"):
        PaymentAppAccountUpdate(
            account_type="checking",  # Wrong type
        )


def test_update_platform_validation():
    """Test platform validation in payment app account update schema."""
    # Test valid platform update
    update = PaymentAppAccountUpdate(
        platform="Revolut",  # Valid platform
    )
    assert update.platform == "Revolut"

    # Test invalid platform update
    with pytest.raises(ValidationError, match="Platform must be one of:"):
        PaymentAppAccountUpdate(
            platform="Invalid Platform",  # Not in allowed values
        )

    # Test None platform (no update)
    update = PaymentAppAccountUpdate(
        platform=None,
    )
    assert update.platform is None


def test_update_card_last_four_validation():
    """Test card last four validation in payment app account update schema."""
    # Test valid update with both fields
    update = PaymentAppAccountUpdate(
        has_debit_card=True,
        card_last_four="4321",
    )
    assert update.has_debit_card is True
    assert update.card_last_four == "4321"

    # Test valid update with only card_last_four when has_debit_card is not being updated
    update = PaymentAppAccountUpdate(
        card_last_four="4321",
        # has_debit_card not provided
    )
    assert update.has_debit_card is None
    assert update.card_last_four == "4321"

    # Test invalid card_last_four (non-numeric)
    with pytest.raises(
        ValidationError, match="Card last four digits must contain only numbers"
    ):
        PaymentAppAccountUpdate(
            card_last_four="abcd",  # Non-numeric
        )

    # Test invalid combination: has_debit_card=False with card_last_four
    with pytest.raises(
        ValidationError,
        match="Card last four digits cannot be provided when debit card is not enabled",
    ):
        PaymentAppAccountUpdate(
            has_debit_card=False,
            card_last_four="4321",  # Should not be provided when has_debit_card is False
        )

    # Test invalid combination: has_debit_card=True without card_last_four
    with pytest.raises(
        ValidationError,
        match="Card last four digits are required when debit card is enabled",
    ):
        PaymentAppAccountUpdate(
            has_debit_card=True,
            # Missing card_last_four
        )


def test_update_linked_account_ids_validation():
    """Test linked account IDs validation in payment app account update schema."""
    # Test valid update
    update = PaymentAppAccountUpdate(
        linked_account_ids="10,20,30",
    )
    assert update.linked_account_ids == "10,20,30"

    # Test with spaces
    update = PaymentAppAccountUpdate(
        linked_account_ids="10, 20, 30",  # Spaces should be trimmed
    )
    assert update.linked_account_ids == "10,20,30"  # Spaces removed

    # Test invalid format (non-numeric)
    with pytest.raises(
        ValidationError,
        match="Linked account IDs must be a comma-separated list of integers",
    ):
        PaymentAppAccountUpdate(
            linked_account_ids="10,twenty,30",  # Non-numeric value
        )

    # Test None value (no update)
    update = PaymentAppAccountUpdate(
        linked_account_ids=None,
    )
    assert update.linked_account_ids is None


def test_update_boolean_fields():
    """Test boolean field updates in payment app account update schema."""
    # Test updating supports_direct_deposit
    update = PaymentAppAccountUpdate(
        supports_direct_deposit=True,
    )
    assert update.supports_direct_deposit is True

    # Test updating supports_crypto
    update = PaymentAppAccountUpdate(
        supports_crypto=True,
    )
    assert update.supports_crypto is True

    # Test updating both boolean fields
    update = PaymentAppAccountUpdate(
        supports_direct_deposit=False,
        supports_crypto=False,
    )
    assert update.supports_direct_deposit is False
    assert update.supports_crypto is False

    # Test None values (no update)
    update = PaymentAppAccountUpdate(
        supports_direct_deposit=None,
        supports_crypto=None,
    )
    assert update.supports_direct_deposit is None
    assert update.supports_crypto is None
