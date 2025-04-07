"""
Unit tests for payments schema factory functions.

Tests ensure that payment schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.schemas.payments import (
    PaymentCreate,
    PaymentDateRange,
    PaymentUpdate,
)
from tests.helpers.schema_factories.payments import (
    create_payment_schema,
    create_payment_update_schema,
    create_payment_date_range_schema,
)
from tests.helpers.schema_factories.payment_sources import (
    create_payment_source_schema,
)


def test_create_payment_schema():
    """Test creating a PaymentCreate schema with default values."""
    schema = create_payment_schema()
    
    assert isinstance(schema, PaymentCreate)
    assert schema.amount == Decimal("100.00")
    assert schema.category == "Bill Payment"
    assert schema.description == "Test payment description"
    assert schema.liability_id is None
    assert schema.income_id is None
    assert isinstance(schema.payment_date, datetime)
    
    # Check that sources were created
    assert len(schema.sources) == 1
    assert schema.sources[0].amount == Decimal("100.00")


def test_create_payment_schema_with_custom_values():
    """Test creating a PaymentCreate schema with custom values."""
    payment_date = datetime(2023, 7, 15, tzinfo=timezone.utc)
    
    schema = create_payment_schema(
        amount=Decimal("250.50"),
        payment_date=payment_date,
        category="Credit Card Payment",
        description="Monthly minimum payment",
        liability_id=1
    )
    
    assert isinstance(schema, PaymentCreate)
    assert schema.amount == Decimal("250.50")
    assert schema.payment_date == payment_date
    assert schema.category == "Credit Card Payment"
    assert schema.description == "Monthly minimum payment"
    assert schema.liability_id == 1
    assert schema.income_id is None
    
    # Check that sources were created with the correct amount
    assert len(schema.sources) == 1
    assert schema.sources[0].amount == Decimal("250.50")


def test_create_payment_schema_with_custom_sources():
    """Test creating a PaymentCreate schema with custom payment sources."""
    sources = [
        create_payment_source_schema(account_id=1, amount=Decimal("75.00")),
        create_payment_source_schema(account_id=2, amount=Decimal("125.00")),
    ]
    
    schema = create_payment_schema(
        amount=Decimal("200.00"),
        sources=sources
    )
    
    assert isinstance(schema, PaymentCreate)
    assert schema.amount == Decimal("200.00")
    assert len(schema.sources) == 2
    
    # Check that our custom sources were used
    assert schema.sources[0].account_id == 1
    assert schema.sources[0].amount == Decimal("75.00")
    assert schema.sources[1].account_id == 2
    assert schema.sources[1].amount == Decimal("125.00")


def test_create_payment_schema_with_sources_as_dict():
    """Test creating a PaymentCreate schema with sources as dictionaries."""
    sources = [
        {"account_id": 3, "amount": Decimal("50.00")},
        {"account_id": 4, "amount": Decimal("150.00")},
    ]
    
    schema = create_payment_schema(
        amount=Decimal("200.00"),
        sources=sources
    )
    
    assert isinstance(schema, PaymentCreate)
    assert schema.amount == Decimal("200.00")
    assert len(schema.sources) == 2
    
    # Check that our dictionary sources were converted to proper schemas
    assert schema.sources[0].account_id == 3
    assert schema.sources[0].amount == Decimal("50.00")
    assert schema.sources[1].account_id == 4
    assert schema.sources[1].amount == Decimal("150.00")


def test_create_payment_update_schema():
    """Test creating a PaymentUpdate schema with minimal values."""
    schema = create_payment_update_schema(id=1)
    
    assert isinstance(schema, PaymentUpdate)
    # In the actual schema, id is not included
    assert schema.amount is None
    assert schema.payment_date is None
    assert schema.category is None
    assert schema.description is None
    assert not hasattr(schema, "sources") or schema.sources is None


def test_create_payment_update_schema_with_all_fields():
    """Test creating a PaymentUpdate schema with all fields."""
    payment_date = datetime(2023, 8, 15, tzinfo=timezone.utc)
    sources = [
        create_payment_source_schema(account_id=5, amount=Decimal("300.00")),
    ]
    
    schema = create_payment_update_schema(
        id=2,  # id is passed to the factory but not used in the schema
        amount=Decimal("300.00"),
        payment_date=payment_date,
        category="Loan Payment",
        description="Extra principal payment",
        sources=sources
    )
    
    assert isinstance(schema, PaymentUpdate)
    # Note: id is not part of the PaymentUpdate schema
    assert schema.amount == Decimal("300.00")
    assert schema.payment_date == payment_date
    assert schema.category == "Loan Payment"
    assert schema.description == "Extra principal payment"
    assert len(schema.sources) == 1
    assert schema.sources[0].account_id == 5
    assert schema.sources[0].amount == Decimal("300.00")


def test_create_payment_update_schema_with_partial_fields():
    """Test creating a PaymentUpdate schema with only some fields."""
    schema = create_payment_update_schema(
        id=3,  # id is passed to the factory but not used in the schema
        amount=Decimal("175.25"),
        description="Updated payment description"
    )
    
    assert isinstance(schema, PaymentUpdate)
    # Note: id is not part of the PaymentUpdate schema
    assert schema.amount == Decimal("175.25")
    assert schema.description == "Updated payment description"
    assert schema.payment_date is None
    assert schema.category is None
    assert not hasattr(schema, "sources") or schema.sources is None


def test_create_payment_date_range_schema():
    """Test creating a PaymentDateRange schema with default values."""
    schema = create_payment_date_range_schema()
    
    assert isinstance(schema, PaymentDateRange)
    assert isinstance(schema.start_date, datetime)
    assert isinstance(schema.end_date, datetime)
    
    # The start date should be the first day of the current month
    assert schema.start_date.day == 1
    
    # End date should be after start date
    assert schema.end_date > schema.start_date


def test_create_payment_date_range_schema_with_custom_values():
    """Test creating a PaymentDateRange schema with custom values."""
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 3, 31, tzinfo=timezone.utc)
    
    schema = create_payment_date_range_schema(
        start_date=start_date,
        end_date=end_date
    )
    
    assert isinstance(schema, PaymentDateRange)
    assert schema.start_date == start_date
    assert schema.end_date == end_date


def test_create_payment_date_range_schema_with_additional_fields():
    """Test creating a PaymentDateRange schema with additional fields via kwargs."""
    # While additional fields are included as kwargs, they don't become
    # attributes in the actual schema, so we only test the core fields
    schema = create_payment_date_range_schema(
        include_pending=True,
        sort_by="date",
        sort_order="desc"
    )
    
    assert isinstance(schema, PaymentDateRange)
    assert isinstance(schema.start_date, datetime)
    assert isinstance(schema.end_date, datetime)
    # These fields don't exist in the schema so we don't assert them
