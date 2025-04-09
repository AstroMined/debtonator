"""
Unit tests for savings account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal

from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.account_types.banking.savings_schema_factories import (
    create_savings_account_response_schema,
    create_savings_account_schema,
)


def test_create_savings_account_schema():
    """Test creating a SavingsAccountCreate schema."""
    schema = create_savings_account_schema()
    assert isinstance(schema, SavingsAccountCreate)
    assert schema.account_type == "savings"
    assert schema.name == "Test Savings Account"
    assert schema.institution == "Test Bank"
    assert schema.interest_rate == Decimal("0.02")  # 2% as decimal
    assert schema.compound_frequency == "monthly"
    assert schema.withdrawal_limit == 6
    assert schema.minimum_balance == Decimal("100.00")


def test_create_savings_account_schema_with_custom_values():
    """Test creating a SavingsAccountCreate schema with custom values."""
    schema = create_savings_account_schema(
        name="High-Yield Savings",
        interest_rate=Decimal("0.035"),  # 3.5% as decimal
        compound_frequency="daily",
        withdrawal_limit=3,
        minimum_balance=Decimal("500.00"),
        interest_earned_ytd=Decimal("75.25"),
    )
    assert schema.name == "High-Yield Savings"
    assert schema.interest_rate == Decimal("0.035")  # 3.5% as decimal
    assert schema.compound_frequency == "daily"
    assert schema.withdrawal_limit == 3
    assert schema.minimum_balance == Decimal("500.00")
    assert schema.interest_earned_ytd == Decimal("75.25")


def test_create_savings_account_response_schema():
    """Test creating a SavingsAccountResponse schema."""
    now = utc_now()
    schema = create_savings_account_response_schema(
        id=456,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, SavingsAccountResponse)
    assert schema.id == 456
    assert schema.account_type == "savings"
    assert schema.created_at == now
    assert schema.updated_at == now
