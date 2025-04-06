"""
Unit tests for balance history schema factory functions.

Tests ensure that balance history schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest

from src.schemas.balance_history import BalanceHistoryCreate, BalanceHistoryUpdate
from tests.helpers.schema_factories.balance_history import (
    create_balance_history_schema,
    create_balance_history_update_schema,
)


def test_create_balance_history_schema():
    """Test creating a BalanceHistoryCreate schema with default values."""
    schema = create_balance_history_schema(account_id=1)
    
    assert isinstance(schema, BalanceHistoryCreate)
    assert schema.account_id == 1
    assert schema.balance == Decimal("1000.00")
    assert schema.is_reconciled is False
    assert schema.available_credit is None
    assert schema.notes is None


def test_create_balance_history_schema_with_custom_values():
    """Test creating a BalanceHistoryCreate schema with custom values."""
    schema = create_balance_history_schema(
        account_id=2,
        balance=Decimal("2500.00"),
        available_credit=Decimal("5000.00"),
        is_reconciled=True,
        notes="Monthly balance update"
    )
    
    assert isinstance(schema, BalanceHistoryCreate)
    assert schema.account_id == 2
    assert schema.balance == Decimal("2500.00")
    assert schema.available_credit == Decimal("5000.00")
    assert schema.is_reconciled is True
    assert schema.notes == "Monthly balance update"


def test_create_balance_history_update_schema_empty():
    """Test creating an empty BalanceHistoryUpdate schema."""
    schema = create_balance_history_update_schema()
    
    assert isinstance(schema, BalanceHistoryUpdate)
    assert schema.balance is None
    assert schema.available_credit is None
    assert schema.is_reconciled is None
    assert schema.notes is None


def test_create_balance_history_update_schema_with_values():
    """Test creating a BalanceHistoryUpdate schema with all fields."""
    schema = create_balance_history_update_schema(
        balance=Decimal("1500.00"),
        available_credit=Decimal("3000.00"),
        is_reconciled=True,
        notes="Updated balance"
    )
    
    assert isinstance(schema, BalanceHistoryUpdate)
    assert schema.balance == Decimal("1500.00")
    assert schema.available_credit == Decimal("3000.00")
    assert schema.is_reconciled is True
    assert schema.notes == "Updated balance"


def test_create_balance_history_update_schema_partial():
    """Test creating a BalanceHistoryUpdate schema with partial fields."""
    schema = create_balance_history_update_schema(
        balance=Decimal("1750.00"),
        notes="Partial update"
    )
    
    assert isinstance(schema, BalanceHistoryUpdate)
    assert schema.balance == Decimal("1750.00")
    assert schema.available_credit is None
    assert schema.is_reconciled is None
    assert schema.notes == "Partial update"
