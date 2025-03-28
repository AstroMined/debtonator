from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from src.constants import DEFAULT_CATEGORY_ID
from src.schemas.liabilities import (
    AutoPaySettings,
    AutoPayUpdate,
    LiabilityCreate,
    LiabilityDateRange,
    LiabilityUpdate,
)
from src.utils.datetime_utils import days_ago, days_from_now, utc_now


def test_liability_create_valid():
    """Test creating a valid liability"""
    due_date = days_from_now(1)
    liability = LiabilityCreate(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=due_date,
        category_id=1,
        primary_account_id=1,
    )
    assert liability.model_dump() == {
        "name": "Test Bill",
        "amount": Decimal("100.00"),
        "due_date": due_date,
        "category_id": 1,
        "primary_account_id": 1,
        "description": None,
        "recurring": False,
        "recurring_bill_id": None,
        "recurrence_pattern": None,
        "auto_pay": False,
        "auto_pay_settings": None,
        "last_auto_pay_attempt": None,
        "auto_pay_enabled": False,
        "paid": False,
    }


def test_liability_create_validates_name_length():
    """Test name length validation"""
    due_date = days_from_now(1)

    # Test empty name
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="",
            amount=Decimal("100.00"),
            due_date=due_date,
            category_id=1,
            primary_account_id=1,
        )
    assert "String should have at least 1 character" in str(exc_info.value)

    # Test too long name
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="x" * 101,
            amount=Decimal("100.00"),
            due_date=due_date,
            category_id=1,
            primary_account_id=1,
        )
    assert "String should have at most 100 characters" in str(exc_info.value)


def test_liability_create_validates_amount():
    """Test amount validation"""
    due_date = days_from_now(1)

    # Test zero amount
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("0.00"),
            due_date=due_date,
            category_id=1,
            primary_account_id=1,
        )
    assert "Input should be greater than 0" in str(exc_info.value)

    # Test negative amount
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("-100.00"),
            due_date=due_date,
            category_id=1,
            primary_account_id=1,
        )
    assert "Input should be greater than 0" in str(exc_info.value)

    # Test too many decimal places
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.001"),
            due_date=due_date,
            category_id=1,
            primary_account_id=1,
        )
    assert "Input should be a multiple of 0.01" in str(exc_info.value)


def test_liability_create_accepts_past_due_date():
    """Test that past due dates are now accepted"""
    # Create a liability with a past due date
    past_date = days_ago(30)  # 30 days in the past
    liability = LiabilityCreate(
        name="Historical Bill",
        amount=Decimal("100.00"),
        due_date=past_date,
        category_id=1,
        primary_account_id=1,
    )
    # Verify it was created successfully with the past due date
    assert liability.due_date == past_date
    assert liability.due_date < datetime.now(timezone.utc)


def test_liability_create_validates_description():
    """Test description validation"""
    due_date = days_from_now(1)

    # Test empty description
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=due_date,
            description="",
            category_id=1,
            primary_account_id=1,
        )
    assert "String should have at least 1 character" in str(exc_info.value)

    # Test too long description
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=due_date,
            description="x" * 501,
            category_id=1,
            primary_account_id=1,
        )
    assert "String should have at most 500 characters" in str(exc_info.value)


def test_liability_create_rejects_naive_datetime():
    """Test naive datetime rejection"""
    """Test that naive datetime is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=datetime(2025, 3, 15),  # Naive datetime
            category_id=1,
            primary_account_id=1,
        )
    assert "Datetime must be UTC" in str(exc_info.value)


def test_liability_create_rejects_non_utc_datetime():
    """Test non-UTC datetime rejection"""
    est_time = datetime(2025, 3, 15, tzinfo=ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=est_time,
            category_id=1,
            primary_account_id=1,
        )
    assert "Datetime must be UTC" in str(exc_info.value)


def test_liability_update_valid():
    """Test valid liability update"""
    due_date = days_from_now(30)  # 30 days in the future
    update = LiabilityUpdate(due_date=due_date, amount=Decimal("150.00"))
    assert update.model_dump() == {
        "name": None,
        "amount": Decimal("150.00"),
        "due_date": due_date,
        "description": None,
        "category_id": None,
        "recurring": None,
        "recurrence_pattern": None,
        "auto_pay": None,
        "auto_pay_settings": None,
        "auto_pay_enabled": None,
    }


def test_liability_update_accepts_past_due_date():
    """Test that a liability update with a past due date is accepted"""
    past_date = days_ago(45)  # 45 days in the past
    update = LiabilityUpdate(
        name="Past Due Bill", due_date=past_date, amount=Decimal("75.50")
    )
    assert update.due_date == past_date
    assert update.due_date < datetime.now(timezone.utc)


def test_liability_update_optional_fields():
    """Test updating a liability with only some fields"""
    update = LiabilityUpdate(amount=Decimal("150.00"))
    assert update.model_dump() == {
        "name": None,
        "amount": Decimal("150.00"),
        "due_date": None,
        "description": None,
        "category_id": None,
        "recurring": None,
        "recurrence_pattern": None,
        "auto_pay": None,
        "auto_pay_settings": None,
        "auto_pay_enabled": None,
    }


def test_liability_create_uses_default_category():
    """Test that LiabilityCreate uses the default category when none is specified."""
    # Create a liability schema without specifying category_id
    liability = LiabilityCreate(
        name="Test Liability",
        amount=Decimal("100.00"),
        due_date=datetime.now(timezone.utc),
        primary_account_id=1,
    )

    # Verify the default category ID is used
    assert liability.category_id == DEFAULT_CATEGORY_ID

    # Create another liability with explicit category_id
    custom_category_id = 5
    liability_with_category = LiabilityCreate(
        name="Test Liability with Category",
        amount=Decimal("100.00"),
        due_date=datetime.now(timezone.utc),
        category_id=custom_category_id,
        primary_account_id=1,
    )

    # Verify the specified category ID is used
    assert liability_with_category.category_id == custom_category_id


def test_auto_pay_settings_validation():
    """Test auto-pay settings validation"""
    # Test valid settings with preferred_pay_date
    settings = AutoPaySettings(
        preferred_pay_date=15,
        payment_method="bank_transfer",
        minimum_balance_required=Decimal("100.00"),
        retry_on_failure=True,
        notification_email="test@example.com",
    )
    assert isinstance(settings, AutoPaySettings)
    assert settings.preferred_pay_date == 15
    assert settings.payment_method == "bank_transfer"
    assert settings.minimum_balance_required == Decimal("100.00")
    assert settings.retry_on_failure is True
    assert settings.notification_email == "test@example.com"
    assert settings.days_before_due is None

    # Test invalid preferred_pay_date (too high)
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(
            preferred_pay_date=32, payment_method="bank_transfer"  # Invalid day
        )
    assert "Input should be less than or equal to 31" in str(exc_info.value)

    # Test invalid days_before_due (too high)
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(days_before_due=31, payment_method="bank_transfer")
    assert "Input should be less than or equal to 30" in str(exc_info.value)

    # Test invalid payment_method (empty)
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(preferred_pay_date=15, payment_method="")
    assert "String should have at least 1 character" in str(exc_info.value)

    # Test invalid payment_method (too long)
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(preferred_pay_date=15, payment_method="x" * 51)
    assert "String should have at most 50 characters" in str(exc_info.value)

    # Test cannot set both preferred_pay_date and days_before_due
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(
            preferred_pay_date=15, days_before_due=5, payment_method="bank_transfer"
        )
    assert "Cannot set both preferred_pay_date and days_before_due" in str(
        exc_info.value
    )


def test_auto_pay_update_validation():
    """Test auto-pay update validation"""
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    assert update.model_dump() == {
        "enabled": True,
        "settings": {
            "preferred_pay_date": None,
            "days_before_due": None,
            "payment_method": "bank_transfer",
            "minimum_balance_required": None,
            "retry_on_failure": True,
            "notification_email": None,
        },
    }


def test_liability_date_range_validation():
    """Test date range validation"""
    now = utc_now()
    # Test valid date range
    start_date = now
    end_date = now + timedelta(days=30)
    date_range = LiabilityDateRange(start_date=start_date, end_date=end_date)
    assert date_range.model_dump() == {"start_date": start_date, "end_date": end_date}

    # Test end date before start date
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(
            start_date=now + timedelta(days=10),
            end_date=now,
        )
    assert "End date must be after start date" in str(exc_info.value)

    # Test same start and end date
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(
            start_date=now,
            end_date=now,
        )
    assert "End date must be after start date" in str(exc_info.value)

    # Test naive datetime rejection
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(
            start_date=datetime.now(),  # Naive datetime
            end_date=now + timedelta(days=10),
        )
    assert "Datetime must be UTC" in str(exc_info.value)

    # Test non-UTC datetime rejection
    est_time = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(start_date=est_time, end_date=now + timedelta(days=10))
    assert "Datetime must be UTC" in str(exc_info.value)
