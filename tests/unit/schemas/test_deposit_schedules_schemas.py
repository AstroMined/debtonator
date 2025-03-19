from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any
import pytest
from pydantic import ValidationError

from src.schemas.deposit_schedules import (
    DepositScheduleBase,
    DepositScheduleCreate,
    DepositScheduleUpdate,
    DepositSchedule
)


# Test valid object creation
def test_deposit_schedule_base_valid():
    """Test valid deposit schedule base schema"""
    now = datetime.now(timezone.utc)
    
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 15},
        status="pending"
    )
    
    assert data.income_id == 1
    assert data.account_id == 2
    assert data.schedule_date == now
    assert data.amount == Decimal("500.00")
    assert data.recurring is True
    assert data.recurrence_pattern == {"frequency": "monthly", "day": 15}
    assert data.status == "pending"


def test_deposit_schedule_base_minimal():
    """Test deposit schedule base schema with minimal fields"""
    now = datetime.now(timezone.utc)
    
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        status="pending"
    )
    
    assert data.income_id == 1
    assert data.account_id == 2
    assert data.schedule_date == now
    assert data.amount == Decimal("500.00")
    assert data.recurring is False
    assert data.recurrence_pattern is None
    assert data.status == "pending"


def test_deposit_schedule_create_valid():
    """Test valid deposit schedule create schema"""
    now = datetime.now(timezone.utc)
    
    data = DepositScheduleCreate(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 15},
        status="pending"
    )
    
    assert data.income_id == 1
    assert data.account_id == 2
    assert data.schedule_date == now
    assert data.amount == Decimal("500.00")
    assert data.recurring is True
    assert data.recurrence_pattern == {"frequency": "monthly", "day": 15}
    assert data.status == "pending"


def test_deposit_schedule_update_valid():
    """Test valid deposit schedule update schema with all fields"""
    now = datetime.now(timezone.utc)
    
    data = DepositScheduleUpdate(
        schedule_date=now,
        amount=Decimal("750.00"),
        recurring=False,
        recurrence_pattern=None,
        status="completed"
    )
    
    assert data.schedule_date == now
    assert data.amount == Decimal("750.00")
    assert data.recurring is False
    assert data.recurrence_pattern is None
    assert data.status == "completed"


def test_deposit_schedule_update_partial():
    """Test deposit schedule update schema with partial fields"""
    # Update only amount
    data1 = DepositScheduleUpdate(amount=Decimal("600.00"))
    assert data1.amount == Decimal("600.00")
    assert data1.schedule_date is None
    assert data1.recurring is None
    assert data1.recurrence_pattern is None
    assert data1.status is None
    
    # Update only status
    data2 = DepositScheduleUpdate(status="completed")
    assert data2.amount is None
    assert data2.schedule_date is None
    assert data2.recurring is None
    assert data2.recurrence_pattern is None
    assert data2.status == "completed"


def test_deposit_schedule_valid():
    """Test valid deposit schedule schema with all fields"""
    now = datetime.now(timezone.utc)
    
    data = DepositSchedule(
        id=1,
        income_id=2,
        account_id=3,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 15},
        status="pending",
        created_at=now,
        updated_at=now
    )
    
    assert data.id == 1
    assert data.income_id == 2
    assert data.account_id == 3
    assert data.schedule_date == now
    assert data.amount == Decimal("500.00")
    assert data.recurring is True
    assert data.recurrence_pattern == {"frequency": "monthly", "day": 15}
    assert data.status == "pending"
    assert data.created_at == now
    assert data.updated_at == now


# Test field validations
def test_required_fields():
    """Test required fields"""
    now = datetime.now(timezone.utc)
    
    # Test missing income_id
    with pytest.raises(ValidationError, match="Field required"):
        DepositScheduleBase(
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.00"),
            status="pending"
        )
    
    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        DepositScheduleBase(
            income_id=1,
            schedule_date=now,
            amount=Decimal("500.00"),
            status="pending"
        )
    
    # Test missing schedule_date
    with pytest.raises(ValidationError, match="Field required"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            amount=Decimal("500.00"),
            status="pending"
        )
    
    # Test missing amount
    with pytest.raises(ValidationError, match="Field required"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            status="pending"
        )
    
    # Test missing status
    with pytest.raises(ValidationError, match="Field required"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.00")
        )


def test_id_field_validation():
    """Test ID field validations"""
    now = datetime.now(timezone.utc)
    
    # Test invalid income_id (not greater than 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        DepositScheduleBase(
            income_id=0,  # Invalid
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.00"),
            status="pending"
        )
    
    # Test invalid account_id (not greater than 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        DepositScheduleBase(
            income_id=1,
            account_id=0,  # Invalid
            schedule_date=now,
            amount=Decimal("500.00"),
            status="pending"
        )


def test_amount_validation():
    """Test amount validation"""
    now = datetime.now(timezone.utc)
    
    # Test amount not greater than 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("0.00"),  # Not greater than 0
            status="pending"
        )
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("-100.00"),  # Negative
            status="pending"
        )
    
    # Test valid amount
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("0.01"),  # Minimum valid amount
        status="pending"
    )
    assert data.amount == Decimal("0.01")


def test_amount_precision_validation():
    """Test amount precision validation"""
    now = datetime.now(timezone.utc)
    
    # Test amount with too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.123"),  # Too many decimal places
            status="pending"
        )
    
    # Test amount with too many decimal places in update
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        DepositScheduleUpdate(amount=Decimal("500.123"))  # Too many decimal places
    
    # Test valid amount precision
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.12"),  # Valid precision
        status="pending"
    )
    assert data.amount == Decimal("500.12")


def test_status_validation():
    """Test status field validation"""
    now = datetime.now(timezone.utc)
    
    # Test invalid status value
    with pytest.raises(ValidationError, match="String should match pattern"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.00"),
            status="in_progress"  # Invalid status
        )
    
    # Test invalid status in update
    with pytest.raises(ValidationError, match="String should match pattern"):
        DepositScheduleUpdate(status="processing")  # Invalid status
    
    # Test valid status values
    for status in ["pending", "completed"]:
        data = DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=now,
            amount=Decimal("500.00"),
            status=status
        )
        assert data.status == status


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now_utc = datetime.now(timezone.utc)
    
    # Test naive datetime in schedule_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        DepositScheduleBase(
            income_id=1,
            account_id=2,
            schedule_date=datetime.now(),  # Naive datetime
            amount=Decimal("500.00"),
            status="pending"
        )
    
    # Test non-UTC timezone in update
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        non_utc_tz = timezone(timedelta(hours=5))
        DepositScheduleUpdate(
            schedule_date=datetime.now().replace(tzinfo=non_utc_tz)  # Non-UTC timezone
        )
    
    # Test naive datetime in timestamps
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        DepositSchedule(
            id=1,
            income_id=2,
            account_id=3,
            schedule_date=now_utc,
            amount=Decimal("500.00"),
            status="pending",
            created_at=datetime.now(),  # Naive datetime
            updated_at=now_utc
        )
    
    # Test valid UTC datetimes
    data = DepositSchedule(
        id=1,
        income_id=2,
        account_id=3,
        schedule_date=now_utc,
        amount=Decimal("500.00"),
        status="pending",
        created_at=now_utc,
        updated_at=now_utc
    )
    # Verify the datetime fields are the same as what we provided (with UTC timezone)
    assert data.schedule_date == now_utc
    assert data.created_at == now_utc
    assert data.updated_at == now_utc


def test_recurrence_pattern():
    """Test recurrence pattern with various formats"""
    now = datetime.now(timezone.utc)
    
    # Test with a complex recurrence pattern
    complex_pattern = {
        "frequency": "weekly",
        "days": [1, 3, 5],  # Monday, Wednesday, Friday
        "end_date": datetime(2025, 12, 31, tzinfo=timezone.utc).isoformat(),
        "occurrences": 52
    }
    
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern=complex_pattern,
        status="pending"
    )
    
    assert data.recurrence_pattern == complex_pattern
    
    # Test with a simple recurrence pattern
    simple_pattern = {
        "frequency": "monthly",
        "day": 15
    }
    
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern=simple_pattern,
        status="pending"
    )
    
    assert data.recurrence_pattern == simple_pattern
    
    # Test recurring=True but no pattern (valid)
    data = DepositScheduleBase(
        income_id=1,
        account_id=2,
        schedule_date=now,
        amount=Decimal("500.00"),
        recurring=True,
        recurrence_pattern=None,  # No pattern provided
        status="pending"
    )
    
    assert data.recurring is True
    assert data.recurrence_pattern is None
