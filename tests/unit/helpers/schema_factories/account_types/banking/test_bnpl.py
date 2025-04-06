"""
Unit tests for Buy Now Pay Later (BNPL) account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest
from decimal import Decimal

from src.utils.datetime_utils import utc_now, utc_datetime
from src.schemas.account_types.banking.bnpl import (
    BNPLAccountCreate,
    BNPLAccountResponse,
)

from tests.helpers.schema_factories.account_types.banking.bnpl import (
    create_bnpl_account_schema,
    create_bnpl_account_response_schema,
)


def test_create_bnpl_account_schema():
    """Test creating a BNPLAccountCreate schema."""
    schema = create_bnpl_account_schema()
    assert isinstance(schema, BNPLAccountCreate)
    assert schema.account_type == "bnpl"
    assert schema.name == "Test BNPL Account"
    assert schema.institution == "Affirm"
    assert schema.bnpl_provider == "Affirm"
    assert schema.original_amount == Decimal("400.00")
    assert schema.installment_count == 4
    assert schema.installments_paid == 0
    assert schema.installment_amount == Decimal("100.00")
    assert schema.payment_frequency == "biweekly"
    assert schema.next_payment_date is not None


def test_create_bnpl_account_schema_with_custom_values():
    """Test creating a BNPLAccountCreate schema with custom values."""
    schema = create_bnpl_account_schema(
        name="Laptop Purchase",
        original_amount=Decimal("1200.00"),
        installment_count=6,
        installments_paid=2,
        installment_amount=Decimal("200.00"),
        payment_frequency="monthly",
        promotion_info="0% interest for 6 months",
        late_fee=Decimal("10.00"),
        bnpl_provider="Klarna",
    )
    assert schema.name == "Laptop Purchase"
    assert schema.original_amount == Decimal("1200.00")
    assert schema.installment_count == 6
    assert schema.installments_paid == 2
    assert schema.installment_amount == Decimal("200.00")
    assert schema.payment_frequency == "monthly"
    assert schema.promotion_info == "0% interest for 6 months"
    assert schema.late_fee == Decimal("10.00")
    assert schema.bnpl_provider == "Klarna"
    assert schema.current_balance == Decimal("800.00")  # 4 remaining installments


def test_create_bnpl_account_response_schema():
    """Test creating a BNPLAccountResponse schema."""
    now = utc_now()
    schema = create_bnpl_account_response_schema(
        id=202,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, BNPLAccountResponse)
    assert schema.id == 202
    assert schema.account_type == "bnpl"
    assert schema.created_at == now
    assert schema.updated_at == now
