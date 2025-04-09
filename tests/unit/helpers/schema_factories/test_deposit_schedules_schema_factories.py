"""
Unit tests for deposit schedule schema factory functions.

Tests ensure that deposit schedule schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

from src.schemas.deposit_schedules import DepositScheduleCreate
from tests.helpers.schema_factories.deposit_schedules_schema_factories import (
    create_deposit_schedule_schema,
)


def test_create_deposit_schedule_schema():
    """Test creating a DepositScheduleCreate schema with default values."""
    schema = create_deposit_schedule_schema(income_id=1, account_id=2)

    assert isinstance(schema, DepositScheduleCreate)
    assert schema.account_id == 2
    assert schema.amount == Decimal("1000.00")
    assert schema.recurring is False
    assert schema.recurrence_pattern is None
    assert schema.status == "pending"
    assert isinstance(schema.schedule_date, datetime)
    assert schema.schedule_date.tzinfo == timezone.utc


def test_create_deposit_schedule_schema_with_custom_values():
    """Test creating a DepositScheduleCreate schema with custom values."""
    schedule_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
    recurrence_pattern = {"frequency": "monthly", "day": 15}

    schema = create_deposit_schedule_schema(
        income_id=1,
        account_id=2,
        schedule_date=schedule_date,
        amount=Decimal("2500.50"),
        recurring=True,
        recurrence_pattern=recurrence_pattern,
        status="completed",
    )

    assert isinstance(schema, DepositScheduleCreate)
    assert schema.account_id == 2
    assert schema.schedule_date == schedule_date
    assert schema.amount == Decimal("2500.50")
    assert schema.recurring is True
    assert schema.recurrence_pattern == recurrence_pattern
    assert schema.status == "completed"


def test_create_deposit_schedule_schema_with_minimum_amount():
    """Test creating a DepositScheduleCreate schema with minimum allowed amount."""
    schema = create_deposit_schedule_schema(
        income_id=1, account_id=2, amount=Decimal("0.01")
    )

    assert isinstance(schema, DepositScheduleCreate)
    assert schema.account_id == 2
    assert schema.amount == Decimal("0.01")


def test_create_deposit_schedule_schema_validates_status():
    """Test that invalid status values are corrected to 'pending'."""
    schema = create_deposit_schedule_schema(
        income_id=1, account_id=2, status="invalid_status"
    )

    assert isinstance(schema, DepositScheduleCreate)
    assert schema.status == "pending"


def test_create_deposit_schedule_schema_with_additional_fields():
    """Test creating a DepositScheduleCreate schema with additional fields."""
    schema = create_deposit_schedule_schema(
        income_id=1, account_id=2, source="Direct Deposit"
    )

    assert isinstance(schema, DepositScheduleCreate)
    assert schema.account_id == 2
    assert schema.source == "Direct Deposit"
