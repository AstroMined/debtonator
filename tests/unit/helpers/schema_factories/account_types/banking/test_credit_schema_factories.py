"""
Unit tests for credit account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest
from decimal import Decimal

from src.utils.datetime_utils import utc_now, utc_datetime
from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
)

from tests.helpers.schema_factories.account_types.banking.credit import (
    create_credit_account_schema,
    create_credit_account_response_schema,
)


def test_create_credit_account_schema():
    """Test creating a CreditAccountCreate schema."""
    schema = create_credit_account_schema()
    assert isinstance(schema, CreditAccountCreate)
    assert schema.account_type == "credit"
    assert schema.name == "Test Credit Card"
    assert schema.institution == "Test Bank"
    assert schema.credit_limit == Decimal("5000.00")
    assert schema.current_balance < 0  # Credit accounts have negative balances
    assert schema.statement_balance is not None
    assert schema.statement_due_date is not None
    assert schema.apr == Decimal("15.99")


def test_create_credit_account_schema_with_custom_values():
    """Test creating a CreditAccountCreate schema with custom values."""
    schema = create_credit_account_schema(
        name="Rewards Card",
        credit_limit=Decimal("10000.00"),
        current_balance=Decimal("-2500.00"),
        statement_balance=Decimal("2500.00"),
        minimum_payment=Decimal("50.00"),
        apr=Decimal("18.99"),
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back",
        autopay_status="minimum",
    )
    assert schema.name == "Rewards Card"
    assert schema.credit_limit == Decimal("10000.00")
    assert schema.current_balance == Decimal("-2500.00")
    assert schema.statement_balance == Decimal("2500.00")
    assert schema.minimum_payment == Decimal("50.00")
    assert schema.apr == Decimal("18.99")
    assert schema.annual_fee == Decimal("95.00")
    assert schema.rewards_program == "Cash Back"
    assert schema.autopay_status == "minimum"


def test_create_credit_account_response_schema():
    """Test creating a CreditAccountResponse schema."""
    now = utc_now()
    schema = create_credit_account_response_schema(
        id=789,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, CreditAccountResponse)
    assert schema.id == 789
    assert schema.account_type == "credit"
    assert schema.created_at == now
    assert schema.updated_at == now
