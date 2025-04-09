"""
Unit tests for payment schedule schema factory functions.

Tests ensure that payment schedule schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.schemas.payment_schedules import PaymentScheduleCreate, PaymentScheduleUpdate
from tests.helpers.schema_factories.payment_schedules_schema_factories import (
    create_payment_schedule_schema,
    create_payment_schedule_update_schema,
)


def test_create_payment_schedule_schema():
    """Test creating a PaymentScheduleCreate schema with default values."""
    schema = create_payment_schedule_schema(liability_id=1, account_id=2)

    assert isinstance(schema, PaymentScheduleCreate)
    assert schema.liability_id == 1
    assert schema.account_id == 2
    assert schema.amount == Decimal("100.00")
    assert schema.auto_process is False
    assert schema.description is None
    assert isinstance(schema.scheduled_date, datetime)
    assert schema.scheduled_date.tzinfo == timezone.utc

    # The scheduled_date should be approximately 7 days in the future
    now = datetime.now(timezone.utc)
    date_diff = schema.scheduled_date - now
    assert 6.9 <= date_diff.total_seconds() / (24 * 3600) <= 7.1


def test_create_payment_schedule_schema_with_custom_values():
    """Test creating a PaymentScheduleCreate schema with custom values."""
    scheduled_date = datetime(2023, 6, 15, tzinfo=timezone.utc)

    schema = create_payment_schedule_schema(
        liability_id=1,
        account_id=2,
        scheduled_date=scheduled_date,
        amount=Decimal("250.75"),
        description="Monthly mortgage payment",
        auto_process=True,
    )

    assert isinstance(schema, PaymentScheduleCreate)
    assert schema.liability_id == 1
    assert schema.account_id == 2
    assert schema.scheduled_date == scheduled_date
    assert schema.amount == Decimal("250.75")
    assert schema.description == "Monthly mortgage payment"
    assert schema.auto_process is True


def test_create_payment_schedule_schema_with_minimum_amount():
    """Test creating a PaymentScheduleCreate schema with minimum allowed amount."""
    schema = create_payment_schedule_schema(
        liability_id=1, account_id=2, amount=Decimal("0.01")
    )

    assert isinstance(schema, PaymentScheduleCreate)
    assert schema.liability_id == 1
    assert schema.account_id == 2
    assert schema.amount == Decimal("0.01")


def test_create_payment_schedule_schema_with_additional_fields():
    """Test creating a PaymentScheduleCreate schema with additional fields."""
    schema = create_payment_schedule_schema(
        liability_id=1,
        account_id=2,
        custom_field="This should be ignored by the schema",
    )

    assert isinstance(schema, PaymentScheduleCreate)
    assert schema.liability_id == 1
    assert schema.account_id == 2

    # The custom_field should not be part of the schema
    with pytest.raises(AttributeError):
        _ = schema.custom_field


def test_create_payment_schedule_update_schema_empty():
    """Test creating an empty PaymentScheduleUpdate schema."""
    schema = create_payment_schedule_update_schema()

    assert isinstance(schema, PaymentScheduleUpdate)
    assert schema.scheduled_date is None
    assert schema.amount is None
    assert schema.account_id is None
    assert schema.description is None
    assert schema.auto_process is None
    assert schema.processed is None


def test_create_payment_schedule_update_schema_with_values():
    """Test creating a PaymentScheduleUpdate schema with all fields."""
    scheduled_date = datetime(2023, 7, 15, tzinfo=timezone.utc)

    schema = create_payment_schedule_update_schema(
        scheduled_date=scheduled_date,
        amount=Decimal("350.00"),
        account_id=3,
        description="Updated payment description",
        auto_process=True,
        processed=True,
    )

    assert isinstance(schema, PaymentScheduleUpdate)
    assert schema.scheduled_date == scheduled_date
    assert schema.amount == Decimal("350.00")
    assert schema.account_id == 3
    assert schema.description == "Updated payment description"
    assert schema.auto_process is True
    assert schema.processed is True


def test_create_payment_schedule_update_schema_partial():
    """Test creating a PaymentScheduleUpdate schema with partial fields."""
    schema = create_payment_schedule_update_schema(
        amount=Decimal("175.50"), description="Partial update"
    )

    assert isinstance(schema, PaymentScheduleUpdate)
    assert schema.scheduled_date is None
    assert schema.amount == Decimal("175.50")
    assert schema.account_id is None
    assert schema.description == "Partial update"
    assert schema.auto_process is None
    assert schema.processed is None
