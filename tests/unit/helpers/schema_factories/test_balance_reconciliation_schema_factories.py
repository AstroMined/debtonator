"""
Unit tests for balance reconciliation schema factory functions.

Tests ensure that balance reconciliation schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal

from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.balance_reconciliation_schema_factories import (
    create_balance_reconciliation_schema,
    create_balance_reconciliation_update_schema,
)


def test_create_balance_reconciliation_schema():
    """Test creating a BalanceReconciliationCreate schema with default values."""
    schema = create_balance_reconciliation_schema(account_id=1)

    assert isinstance(schema, BalanceReconciliationCreate)
    assert schema.account_id == 1
    assert schema.previous_balance == Decimal("1000.00")
    assert schema.new_balance == Decimal("1100.00")
    assert schema.adjustment_amount == Decimal("100.00")  # Should be calculated
    assert schema.reason == "Balance correction"
    # Note: reconciliation_date is passed to the factory but not part of the schema


def test_create_balance_reconciliation_schema_with_custom_values():
    """Test creating a BalanceReconciliationCreate schema with custom values."""
    now = utc_now()
    schema = create_balance_reconciliation_schema(
        account_id=2,
        previous_balance=Decimal("2000.00"),
        new_balance=Decimal("1500.00"),
        reason="Overdraft adjustment",
        reconciliation_date=now,  # Passed to factory but not part of the schema
    )

    assert isinstance(schema, BalanceReconciliationCreate)
    assert schema.account_id == 2
    assert schema.previous_balance == Decimal("2000.00")
    assert schema.new_balance == Decimal("1500.00")
    assert schema.adjustment_amount == Decimal("-500.00")  # Should be calculated
    assert schema.reason == "Overdraft adjustment"
    # Note: reconciliation_date is used in factory but not part of final schema


def test_create_balance_reconciliation_schema_adjustment_calculation():
    """Test that the adjustment_amount is correctly calculated."""
    # Test positive adjustment
    schema = create_balance_reconciliation_schema(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
    )
    assert schema.adjustment_amount == Decimal("200.00")

    # Test negative adjustment
    schema = create_balance_reconciliation_schema(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("800.00"),
    )
    assert schema.adjustment_amount == Decimal("-200.00")

    # Test zero adjustment
    schema = create_balance_reconciliation_schema(
        account_id=1,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1000.00"),
    )
    assert schema.adjustment_amount == Decimal("0.00")


def test_create_balance_reconciliation_update_schema():
    """Test creating a BalanceReconciliationUpdate schema with minimal fields."""
    # Note: id is passed to the factory function but not included in the schema
    schema = create_balance_reconciliation_update_schema(id=1)

    assert isinstance(schema, BalanceReconciliationUpdate)
    assert schema.new_balance is None
    assert schema.reason is None
    assert schema.adjustment_amount is None


def test_create_balance_reconciliation_update_schema_with_values():
    """Test creating a BalanceReconciliationUpdate schema with all fields."""
    # Note: id is passed to the factory function but not included in the schema
    schema = create_balance_reconciliation_update_schema(
        id=2,  # Used by factory but not included in schema
        new_balance=Decimal("1750.00"),
        reason="Corrected balance",
        adjustment_amount=Decimal("250.00"),
    )

    assert isinstance(schema, BalanceReconciliationUpdate)
    assert schema.new_balance == Decimal("1750.00")
    assert schema.reason == "Corrected balance"
    assert schema.adjustment_amount == Decimal("250.00")


def test_create_balance_reconciliation_update_schema_partial():
    """Test creating a BalanceReconciliationUpdate schema with partial fields."""
    # Note: id is passed to the factory function but not included in the schema
    schema = create_balance_reconciliation_update_schema(
        id=3,  # Used by factory but not included in schema
        new_balance=Decimal("2500.00"),
    )

    assert isinstance(schema, BalanceReconciliationUpdate)
    assert schema.new_balance == Decimal("2500.00")
    assert schema.reason is None
    assert schema.adjustment_amount is None
