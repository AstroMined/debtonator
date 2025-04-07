"""
Unit tests for payment app account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest
from decimal import Decimal

from src.utils.datetime_utils import utc_now, utc_datetime
from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
)

from tests.helpers.schema_factories.account_types.banking.payment_app import (
    create_payment_app_account_schema,
    create_payment_app_account_response_schema,
)


def test_create_payment_app_account_schema():
    """Test creating a PaymentAppAccountCreate schema."""
    schema = create_payment_app_account_schema()
    assert isinstance(schema, PaymentAppAccountCreate)
    assert schema.account_type == "payment_app"
    assert schema.name == "Test Payment App"
    assert schema.institution == "PayPal"
    assert schema.platform == "PayPal"
    assert schema.has_debit_card is False
    assert schema.supports_direct_deposit is True
    assert schema.supports_crypto is False


def test_create_payment_app_account_schema_with_debit_card():
    """Test creating a PaymentAppAccountCreate schema with debit card."""
    schema = create_payment_app_account_schema(
        has_debit_card=True,
        card_last_four="4321",
    )
    assert schema.has_debit_card is True
    assert schema.card_last_four == "4321"


def test_create_payment_app_account_schema_with_linked_accounts():
    """Test creating a PaymentAppAccountCreate schema with linked accounts."""
    schema = create_payment_app_account_schema(
        platform="Venmo",
        linked_account_ids="123,456,789",
        supports_crypto=True,
    )
    assert schema.platform == "Venmo"
    assert schema.linked_account_ids == "123,456,789"
    assert schema.supports_crypto is True


def test_create_payment_app_account_response_schema():
    """Test creating a PaymentAppAccountResponse schema."""
    now = utc_now()
    schema = create_payment_app_account_response_schema(
        id=101,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, PaymentAppAccountResponse)
    assert schema.id == 101
    assert schema.account_type == "payment_app"
    assert schema.created_at == now
    assert schema.updated_at == now
