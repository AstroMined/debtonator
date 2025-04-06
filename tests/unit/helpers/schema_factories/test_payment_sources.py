"""
Unit tests for payment source schema factory functions.

Tests ensure that payment source schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest

from src.schemas.payments import PaymentSourceCreate, PaymentSourceUpdate
from tests.helpers.schema_factories.payment_sources import (
    create_payment_source_schema,
    create_payment_source_update_schema,
)


def test_create_payment_source_schema_default():
    """Test creating a PaymentSourceCreate schema with default values."""
    schema = create_payment_source_schema()
    
    assert isinstance(schema, PaymentSourceCreate)
    assert schema.account_id == 1
    assert schema.amount == Decimal("100.00")


def test_create_payment_source_schema_custom():
    """Test creating a PaymentSourceCreate schema with custom values."""
    schema = create_payment_source_schema(
        account_id=5,
        amount=Decimal("250.50")
    )
    
    assert isinstance(schema, PaymentSourceCreate)
    assert schema.account_id == 5
    assert schema.amount == Decimal("250.50")


def test_create_payment_source_update_schema_minimal():
    """Test creating a PaymentSourceUpdate schema with minimal fields."""
    # Note: id is passed to the factory but not part of the schema
    schema = create_payment_source_update_schema(id=1)
    
    assert isinstance(schema, PaymentSourceUpdate)
    assert schema.account_id is None
    assert schema.amount is None
    assert schema.payment_id is None


def test_create_payment_source_update_schema_full():
    """Test creating a PaymentSourceUpdate schema with all fields."""
    # Note: id is passed to the factory but not part of the schema
    schema = create_payment_source_update_schema(
        id=2,  # Used by factory but not in schema
        account_id=10,
        amount=Decimal("300.00"),
        payment_id=5
    )
    
    assert isinstance(schema, PaymentSourceUpdate)
    assert schema.account_id == 10
    assert schema.amount == Decimal("300.00")
    assert schema.payment_id == 5


def test_create_payment_source_update_schema_partial():
    """Test creating a PaymentSourceUpdate schema with partial fields."""
    # Note: id is passed to the factory but not part of the schema
    schema = create_payment_source_update_schema(
        id=3,  # Used by factory but not in schema
        amount=Decimal("150.75")
    )
    
    assert isinstance(schema, PaymentSourceUpdate)
    assert schema.account_id is None
    assert schema.amount == Decimal("150.75")
    assert schema.payment_id is None
