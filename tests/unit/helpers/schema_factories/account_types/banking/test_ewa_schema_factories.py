"""
Unit tests for Earned Wage Access (EWA) account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import timedelta
from decimal import Decimal

from src.schemas.account_types.banking.ewa import EWAAccountCreate, EWAAccountResponse
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.account_types.banking.ewa_schema_factories import (
    create_ewa_account_response_schema,
    create_ewa_account_schema,
)


def test_create_ewa_account_schema():
    """Test creating an EWAAccountCreate schema."""
    schema = create_ewa_account_schema()
    assert isinstance(schema, EWAAccountCreate)
    assert schema.account_type == "ewa"
    assert schema.name == "Test EWA Account"
    assert schema.institution == "DailyPay"
    assert schema.provider == "DailyPay"
    assert schema.max_advance_percentage == Decimal("50.0")
    assert schema.per_transaction_fee == Decimal("1.99")
    assert schema.pay_period_start is not None
    assert schema.pay_period_end is not None
    assert schema.next_payday is not None
    assert schema.pay_period_end > schema.pay_period_start
    assert schema.next_payday > schema.pay_period_end


def test_create_ewa_account_schema_with_custom_values():
    """Test creating an EWAAccountCreate schema with custom values."""
    now = utc_now()
    pay_period_start = now - timedelta(days=10)
    pay_period_end = now + timedelta(days=4)
    next_payday = pay_period_end + timedelta(days=2)

    schema = create_ewa_account_schema(
        name="Early Pay Access",
        provider="Payactiv",
        max_advance_percentage=Decimal("40.0"),
        per_transaction_fee=Decimal("2.50"),
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        next_payday=next_payday,
    )
    assert schema.name == "Early Pay Access"
    assert schema.provider == "Payactiv"
    assert schema.max_advance_percentage == Decimal("40.0")
    assert schema.per_transaction_fee == Decimal("2.50")
    assert schema.pay_period_start == pay_period_start
    assert schema.pay_period_end == pay_period_end
    assert schema.next_payday == next_payday


def test_create_ewa_account_response_schema():
    """Test creating an EWAAccountResponse schema."""
    now = utc_now()
    schema = create_ewa_account_response_schema(
        id=303,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, EWAAccountResponse)
    assert schema.id == 303
    assert schema.account_type == "ewa"
    assert schema.created_at == now
    assert schema.updated_at == now
