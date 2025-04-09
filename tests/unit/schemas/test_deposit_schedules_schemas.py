"""
Tests for deposit schedule schemas.

Validates proper schema validation for deposit schedule creation, updates,
and response formatting.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.deposit_schedules import (
    DepositScheduleCreate,
    DepositScheduleResponse,
    DepositScheduleUpdate,
)
from src.utils.datetime_utils import utc_datetime, utc_now


def test_deposit_schedule_create_valid():
    """Test creating a valid deposit schedule."""
    # Using utc_now for proper timezone handling
    schedule_date = utc_now()

    deposit_schedule = DepositScheduleCreate(
        schedule_date=schedule_date,
        amount=Decimal("750.00"),
        account_id=1,
        source="Direct Deposit",
        recurring=True,
        recurrence_pattern={
            "frequency": "monthly",
            "interval": 1,
            "day_of_month": 15,
        },
    )

    assert deposit_schedule.schedule_date == schedule_date
    assert deposit_schedule.amount == Decimal("750.00")
    assert deposit_schedule.account_id == 1
    assert deposit_schedule.source == "Direct Deposit"
    assert deposit_schedule.recurring is True
    assert deposit_schedule.recurrence_pattern == {
        "frequency": "monthly",
        "interval": 1,
        "day_of_month": 15,
    }


def test_deposit_schedule_create_minimum_fields():
    """Test creating a deposit schedule with minimum required fields."""
    # Using utc_datetime for proper timezone handling
    schedule_date = utc_datetime(2025, 4, 15, 14, 0, 0)

    deposit_schedule = DepositScheduleCreate(
        schedule_date=schedule_date,
        amount=Decimal("500.00"),
        account_id=1,
    )

    assert deposit_schedule.schedule_date == schedule_date
    assert deposit_schedule.amount == Decimal("500.00")
    assert deposit_schedule.account_id == 1
    assert deposit_schedule.source == "Other"  # Default value
    assert deposit_schedule.recurring is False  # Default value
    assert deposit_schedule.recurrence_pattern is None  # Default value


def test_deposit_schedule_create_invalid_amount():
    """Test validation for invalid amount."""
    schedule_date = utc_now()

    # Test negative amount
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("-100.00"),
            account_id=1,
        )
    assert "Input should be greater than 0" in str(exc_info.value)

    # Test zero amount
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("0.00"),
            account_id=1,
        )
    assert "Input should be greater than 0" in str(exc_info.value)

    # Test too many decimal places
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("100.001"),
            account_id=1,
        )
    assert "Input should be a multiple of 0.01" in str(exc_info.value)


def test_deposit_schedule_create_invalid_source():
    """Test validation for invalid source."""
    schedule_date = utc_now()

    # Test empty source
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("100.00"),
            account_id=1,
            source="",
        )
    assert "String should have at least 1 character" in str(exc_info.value)

    # Test too long source
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("100.00"),
            account_id=1,
            source="x" * 101,  # 101 characters
        )
    assert "String should have at most 100 characters" in str(exc_info.value)


def test_deposit_schedule_update_valid():
    """Test valid deposit schedule update."""
    # Using utc_now for proper timezone handling
    schedule_date = utc_now()

    # Create a valid update with only the desired fields
    update = DepositScheduleUpdate(
        schedule_date=schedule_date,
        amount=Decimal("750.00"),
        recurring=False,
        status="completed",
    )

    # Verify the update data is correct
    assert update.schedule_date == schedule_date
    assert update.amount == Decimal("750.00")
    assert update.recurring is False
    assert update.status == "completed"
    assert update.recurrence_pattern is None  # Not included in update


def test_deposit_schedule_update_invalid_status():
    """Test invalid status validation in update."""
    # Using utc_now for proper timezone handling
    schedule_date = utc_now()

    # Test with invalid status value
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleUpdate(
            schedule_date=schedule_date,
            status="invalid_status",  # Not in allowed enum
        )
    # Check for pattern mismatch error - updated to match actual Pydantic v2 error message
    assert "String should match pattern" in str(exc_info.value)


def test_deposit_schedule_recurring_validation():
    """Test recurrence pattern validation."""
    # Using utc_now for proper timezone handling
    schedule_date = utc_now()

    # Test missing recurrence_pattern when recurring=True
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("750.00"),
            account_id=1,
            recurring=True,  # Requires recurrence_pattern
        )
    assert "Recurrence pattern is required when recurring is True" in str(
        exc_info.value
    )

    # Test with recurrence_pattern when recurring=False
    with pytest.raises(ValidationError) as exc_info:
        DepositScheduleCreate(
            schedule_date=schedule_date,
            amount=Decimal("750.00"),
            account_id=1,
            recurring=False,
            recurrence_pattern={
                "frequency": "monthly",
                "interval": 1,
                "day_of_month": 15,
            },
        )
    assert "Recurrence pattern should not be provided when recurring is False" in str(
        exc_info.value
    )


def test_deposit_schedule_response_format():
    """Test deposit schedule response format."""
    # Using utc_datetime for proper timezone handling
    schedule_date = utc_datetime(2025, 4, 15, 14, 0, 0)
    created_at = utc_datetime(2025, 4, 1, 10, 0, 0)
    updated_at = utc_datetime(2025, 4, 1, 10, 0, 0)

    # Create a response object
    response = DepositScheduleResponse(
        id=1,
        schedule_date=schedule_date,
        amount=Decimal("750.00"),
        account_id=1,
        source="Direct Deposit",
        recurring=True,
        recurrence_pattern={
            "frequency": "monthly",
            "interval": 1,
            "day_of_month": 15,
        },
        status="pending",
        created_at=created_at,
        updated_at=updated_at,
    )

    # Convert to dict and verify format
    response_dict = response.model_dump(mode="json")

    # Check timestamps are in ISO format with Z suffix
    assert "Z" in response_dict["schedule_date"]
    assert "Z" in response_dict["created_at"]
    assert "Z" in response_dict["updated_at"]

    # Check other fields
    assert response_dict["id"] == 1
    assert response_dict["amount"] == 750.00  # Converted to float for JSON
    assert response_dict["account_id"] == 1
    assert response_dict["source"] == "Direct Deposit"
    assert response_dict["recurring"] is True
    assert response_dict["status"] == "pending"
