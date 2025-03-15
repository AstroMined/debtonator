from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from pydantic import ValidationError

from src.schemas.payment_schedules import (
    PaymentScheduleBase,
    PaymentScheduleCreate,
    PaymentScheduleUpdate,
    PaymentSchedule
)


# Test valid object creation
def test_payment_schedule_base_valid():
    """Test valid payment schedule base schema"""
    now = datetime.now(timezone.utc)
    
    data = PaymentScheduleBase(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("150.75"),
        description="Monthly car payment",
        auto_process=True
    )
    
    assert data.liability_id == 1
    assert data.account_id == 2
    assert data.scheduled_date == now
    assert data.amount == Decimal("150.75")
    assert data.description == "Monthly car payment"
    assert data.auto_process is True


def test_payment_schedule_base_minimal():
    """Test payment schedule base schema with only required fields"""
    now = datetime.now(timezone.utc)
    
    data = PaymentScheduleBase(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("150.75")
    )
    
    assert data.liability_id == 1
    assert data.account_id == 2
    assert data.scheduled_date == now
    assert data.amount == Decimal("150.75")
    assert data.description is None
    assert data.auto_process is False


def test_payment_schedule_create_valid():
    """Test valid payment schedule create schema"""
    now = datetime.now(timezone.utc)
    
    data = PaymentScheduleCreate(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("150.75"),
        description="Monthly car payment",
        auto_process=True
    )
    
    assert data.liability_id == 1
    assert data.account_id == 2
    assert data.scheduled_date == now
    assert data.amount == Decimal("150.75")
    assert data.description == "Monthly car payment"
    assert data.auto_process is True


def test_payment_schedule_update_valid():
    """Test valid payment schedule update schema with all fields"""
    now = datetime.now(timezone.utc)
    
    data = PaymentScheduleUpdate(
        scheduled_date=now,
        amount=Decimal("200.50"),
        account_id=3,
        description="Updated car payment",
        auto_process=False,
        processed=True
    )
    
    assert data.scheduled_date == now
    assert data.amount == Decimal("200.50")
    assert data.account_id == 3
    assert data.description == "Updated car payment"
    assert data.auto_process is False
    assert data.processed is True


def test_payment_schedule_update_partial():
    """Test payment schedule update schema with partial fields"""
    # Update only amount
    data1 = PaymentScheduleUpdate(amount=Decimal("175.25"))
    assert data1.amount == Decimal("175.25")
    assert data1.scheduled_date is None
    assert data1.account_id is None
    assert data1.description is None
    assert data1.auto_process is None
    assert data1.processed is None
    
    # Update only processed status
    data2 = PaymentScheduleUpdate(processed=True)
    assert data2.amount is None
    assert data2.scheduled_date is None
    assert data2.account_id is None
    assert data2.description is None
    assert data2.auto_process is None
    assert data2.processed is True


def test_payment_schedule_valid():
    """Test valid payment schedule schema with all fields"""
    now = datetime.now(timezone.utc)
    processed_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
    
    data = PaymentSchedule(
        id=1,
        liability_id=2,
        account_id=3,
        scheduled_date=now,
        amount=Decimal("150.75"),
        description="Monthly car payment",
        auto_process=True,
        processed=True,
        processed_date=processed_date,
        created_at=now,
        updated_at=now
    )
    
    assert data.id == 1
    assert data.liability_id == 2
    assert data.account_id == 3
    assert data.scheduled_date == now
    assert data.amount == Decimal("150.75")
    assert data.description == "Monthly car payment"
    assert data.auto_process is True
    assert data.processed is True
    assert data.processed_date == processed_date
    assert data.created_at == now
    assert data.updated_at == now


def test_payment_schedule_unprocessed():
    """Test valid payment schedule schema that hasn't been processed"""
    now = datetime.now(timezone.utc)
    
    data = PaymentSchedule(
        id=1,
        liability_id=2,
        account_id=3,
        scheduled_date=now,
        amount=Decimal("150.75"),
        description="Monthly car payment",
        auto_process=True,
        processed=False,  # Not processed
        processed_date=None,  # No processed date
        created_at=now,
        updated_at=now
    )
    
    assert data.id == 1
    assert data.processed is False
    assert data.processed_date is None


# Test field validations
def test_required_fields():
    """Test required fields"""
    now = datetime.now(timezone.utc)
    
    # Test missing liability_id
    with pytest.raises(ValidationError, match="Field required"):
        PaymentScheduleBase(
            account_id=2,
            scheduled_date=now,
            amount=Decimal("150.75")
        )
    
    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        PaymentScheduleBase(
            liability_id=1,
            scheduled_date=now,
            amount=Decimal("150.75")
        )
    
    # Test missing scheduled_date
    with pytest.raises(ValidationError, match="Field required"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            amount=Decimal("150.75")
        )
    
    # Test missing amount
    with pytest.raises(ValidationError, match="Field required"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=now
        )


def test_id_field_validation():
    """Test ID field validations"""
    now = datetime.now(timezone.utc)
    
    # Test invalid liability_id (not greater than 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentScheduleBase(
            liability_id=0,  # Invalid
            account_id=2,
            scheduled_date=now,
            amount=Decimal("150.75")
        )
    
    # Test invalid account_id (not greater than 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=0,  # Invalid
            scheduled_date=now,
            amount=Decimal("150.75")
        )
    
    # Test invalid account_id in update (not greater than 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentScheduleUpdate(account_id=0)  # Invalid


def test_description_length_validation():
    """Test description length validation"""
    now = datetime.now(timezone.utc)
    
    # Test description too long
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=now,
            amount=Decimal("150.75"),
            description="X" * 501  # Too long
        )
    
    # Test valid description length boundary
    data = PaymentScheduleBase(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("150.75"),
        description="X" * 500  # Exactly 500 characters
    )
    assert len(data.description) == 500


# Test amount validation
def test_amount_validation():
    """Test amount validation"""
    now = datetime.now(timezone.utc)
    
    # Test amount not greater than 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=now,
            amount=Decimal("0.00")  # Not greater than 0
        )
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=now,
            amount=Decimal("-10.00")  # Negative
        )
    
    # Test valid amount
    data = PaymentScheduleBase(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("0.01")  # Minimum valid amount
    )
    assert data.amount == Decimal("0.01")


def test_amount_precision_validation():
    """Test amount precision validation"""
    now = datetime.now(timezone.utc)
    
    # Test amount with too many decimal places
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=now,
            amount=Decimal("150.756")  # Too many decimal places
        )
    
    # Test amount with too many decimal places in update
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        PaymentScheduleUpdate(amount=Decimal("150.756"))  # Too many decimal places
    
    # Test valid amount precision
    data = PaymentScheduleBase(
        liability_id=1,
        account_id=2,
        scheduled_date=now,
        amount=Decimal("150.75")  # Valid precision
    )
    assert data.amount == Decimal("150.75")


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now_utc = datetime.now(timezone.utc)
    
    # Test naive datetime in scheduled_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentScheduleBase(
            liability_id=1,
            account_id=2,
            scheduled_date=datetime.now(),  # Naive datetime
            amount=Decimal("150.75")
        )
    
    # Test non-UTC timezone in update
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        non_utc_tz = timezone(timedelta(hours=5))
        PaymentScheduleUpdate(
            scheduled_date=datetime.now().replace(tzinfo=non_utc_tz)  # Non-UTC timezone
        )
    
    # Test naive datetime in PaymentSchedule
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentSchedule(
            id=1,
            liability_id=2,
            account_id=3,
            scheduled_date=now_utc,
            amount=Decimal("150.75"),
            processed=False,
            created_at=datetime.now(),  # Naive datetime
            updated_at=now_utc
        )
    
    # Test valid UTC datetimes
    data = PaymentSchedule(
        id=1,
        liability_id=2,
        account_id=3,
        scheduled_date=now_utc,
        amount=Decimal("150.75"),
        processed=False,
        created_at=now_utc,
        updated_at=now_utc
    )
    # Verify the datetime fields are the same as what we provided (with UTC timezone)
    assert data.scheduled_date == now_utc
    assert data.created_at == now_utc
    assert data.updated_at == now_utc
