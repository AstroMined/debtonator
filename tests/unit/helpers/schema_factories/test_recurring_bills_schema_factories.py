"""
Unit tests for recurring bill schema factory functions.

Tests ensure that recurring bill schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime
from decimal import Decimal

import pytest

from src.schemas.recurring_bills import (
    GenerateBillsRequest,
    RecurringBillCreate,
    RecurringBillResponse,
    RecurringBillUpdate,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.recurring_bills import (
    create_recurring_bill_schema,
    create_recurring_bill_update_schema,
    create_recurring_bill_response_schema,
    create_generate_bills_request_schema,
)


def test_create_recurring_bill_schema():
    """Test creating a RecurringBillCreate schema with default values."""
    schema = create_recurring_bill_schema(account_id=1, category_id=2)
    
    assert isinstance(schema, RecurringBillCreate)
    assert schema.account_id == 1
    assert schema.category_id == 2
    assert schema.bill_name == "Test Monthly Bill"
    assert schema.amount == Decimal("100.00")
    assert schema.day_of_month == 15
    assert schema.auto_pay is False


def test_create_recurring_bill_schema_with_custom_values():
    """Test creating a RecurringBillCreate schema with custom values."""
    schema = create_recurring_bill_schema(
        account_id=3,
        category_id=4,
        bill_name="Electricity Bill",
        amount=Decimal("85.50"),
        day_of_month=20,
        auto_pay=True
    )
    
    assert isinstance(schema, RecurringBillCreate)
    assert schema.account_id == 3
    assert schema.category_id == 4
    assert schema.bill_name == "Electricity Bill"
    assert schema.amount == Decimal("85.50")
    assert schema.day_of_month == 20
    assert schema.auto_pay is True


def test_create_recurring_bill_update_schema_empty():
    """Test creating a RecurringBillUpdate schema with no specified fields."""
    schema = create_recurring_bill_update_schema(id=1)
    
    assert isinstance(schema, RecurringBillUpdate)
    # The schema should be created but have no fields set
    assert len(schema.model_dump(exclude_none=True)) == 0


def test_create_recurring_bill_update_schema_with_all_fields():
    """Test creating a RecurringBillUpdate schema with all fields specified."""
    schema = create_recurring_bill_update_schema(
        id=2,
        bill_name="Updated Utilities",
        amount=Decimal("150.75"),
        day_of_month=25,
        account_id=5,
        category_id=6,
        auto_pay=True,
        active=False
    )
    
    assert isinstance(schema, RecurringBillUpdate)
    assert schema.bill_name == "Updated Utilities"
    assert schema.amount == Decimal("150.75")
    assert schema.day_of_month == 25
    assert schema.account_id == 5
    assert schema.category_id == 6
    assert schema.auto_pay is True
    assert schema.active is False


def test_create_recurring_bill_update_schema_with_partial_fields():
    """Test creating a RecurringBillUpdate schema with some fields specified."""
    schema = create_recurring_bill_update_schema(
        id=3,
        bill_name="Updated Internet",
        amount=Decimal("75.00")
    )
    
    assert isinstance(schema, RecurringBillUpdate)
    assert schema.bill_name == "Updated Internet"
    assert schema.amount == Decimal("75.00")
    assert schema.day_of_month is None
    assert schema.account_id is None
    assert schema.category_id is None
    assert schema.auto_pay is None
    assert schema.active is None


def test_create_recurring_bill_response_schema():
    """Test creating a RecurringBillResponse schema with default values."""
    schema = create_recurring_bill_response_schema(id=4, account_id=7, category_id=8)
    
    assert isinstance(schema, RecurringBillResponse)
    assert schema.id == 4
    assert schema.account_id == 7
    assert schema.category_id == 8
    assert schema.bill_name == "Test Monthly Bill"
    assert schema.amount == Decimal("100.00")
    assert schema.day_of_month == 15
    assert schema.auto_pay is False
    assert schema.active is True
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_create_recurring_bill_response_schema_with_custom_values():
    """Test creating a RecurringBillResponse schema with custom values."""
    created_at = utc_now()
    updated_at = utc_now()
    
    schema = create_recurring_bill_response_schema(
        id=5,
        account_id=9,
        category_id=10,
        bill_name="Internet Service",
        amount=Decimal("95.00"),
        day_of_month=5,
        auto_pay=True,
        active=False,
        created_at=created_at,
        updated_at=updated_at
    )
    
    assert isinstance(schema, RecurringBillResponse)
    assert schema.id == 5
    assert schema.account_id == 9
    assert schema.category_id == 10
    assert schema.bill_name == "Internet Service"
    assert schema.amount == Decimal("95.00")
    assert schema.day_of_month == 5
    assert schema.auto_pay is True
    assert schema.active is False
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at


def test_create_generate_bills_request_schema():
    """Test creating a GenerateBillsRequest schema with default values."""
    schema = create_generate_bills_request_schema()
    
    assert isinstance(schema, GenerateBillsRequest)
    assert schema.month == 1
    assert schema.year == 2025


def test_create_generate_bills_request_schema_with_custom_values():
    """Test creating a GenerateBillsRequest schema with custom values."""
    schema = create_generate_bills_request_schema(
        month=6,
        year=2023
    )
    
    assert isinstance(schema, GenerateBillsRequest)
    assert schema.month == 6
    assert schema.year == 2023