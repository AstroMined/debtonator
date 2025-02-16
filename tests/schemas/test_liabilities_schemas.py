from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from pydantic import ValidationError

from src.schemas.liabilities import (
    LiabilityCreate,
    LiabilityUpdate,
    AutoPaySettings,
    AutoPayUpdate,
    LiabilityDateRange
)

def test_liability_create_with_utc_datetime():
    """Test creating a liability with UTC datetime"""
    liability = LiabilityCreate(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
        category_id=1,
        primary_account_id=1
    )
    assert liability.due_date.tzinfo == ZoneInfo("UTC")

def test_liability_create_rejects_naive_datetime():
    """Test that naive datetime is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=datetime(2025, 3, 15),  # Naive datetime
            category_id=1,
            primary_account_id=1
        )
    assert "Datetime must be UTC" in str(exc_info.value)

def test_liability_create_rejects_non_utc_datetime():
    """Test that non-UTC datetime is rejected"""
    est_time = datetime(2025, 3, 15, tzinfo=ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError) as exc_info:
        LiabilityCreate(
            name="Test Bill",
            amount=Decimal("100.00"),
            due_date=est_time,
            category_id=1,
            primary_account_id=1
        )
    assert "Datetime must be UTC" in str(exc_info.value)

def test_liability_update_with_utc_datetime():
    """Test updating a liability with UTC datetime"""
    update = LiabilityUpdate(
        due_date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
        amount=Decimal("150.00")
    )
    assert update.due_date.tzinfo == ZoneInfo("UTC")

def test_liability_update_optional_fields():
    """Test updating a liability with only some fields"""
    update = LiabilityUpdate(amount=Decimal("150.00"))
    assert update.amount == Decimal("150.00")
    assert update.due_date is None
    assert update.name is None

def test_auto_pay_settings_validation():
    """Test auto-pay settings validation"""
    # Test valid settings
    settings = AutoPaySettings(
        preferred_pay_date=15,
        days_before_due=5,
        payment_method="bank_transfer",
        minimum_balance_required=Decimal("100.00"),
        retry_on_failure=True,
        notification_email="test@example.com"
    )
    assert settings.preferred_pay_date == 15
    assert settings.payment_method == "bank_transfer"

    # Test invalid preferred_pay_date
    with pytest.raises(ValidationError) as exc_info:
        AutoPaySettings(
            preferred_pay_date=32,  # Invalid day
            payment_method="bank_transfer"
        )
    assert "Input should be less than or equal to 31" in str(exc_info.value)

def test_auto_pay_update_validation():
    """Test auto-pay update validation"""
    settings = AutoPaySettings(payment_method="bank_transfer")
    update = AutoPayUpdate(enabled=True, settings=settings)
    assert update.enabled is True
    assert update.settings.payment_method == "bank_transfer"

def test_liability_date_range_validation():
    """Test date range validation"""
    # Test valid date range
    date_range = LiabilityDateRange(
        start_date=datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC")),
        end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC"))
    )
    assert date_range.start_date.tzinfo == ZoneInfo("UTC")
    assert date_range.end_date.tzinfo == ZoneInfo("UTC")

    # Test naive datetime rejection
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(
            start_date=datetime(2025, 1, 1),  # Naive datetime
            end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC"))
        )
    assert "Datetime must be UTC" in str(exc_info.value)

    # Test non-UTC datetime rejection
    est_time = datetime(2025, 1, 1, tzinfo=ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError) as exc_info:
        LiabilityDateRange(
            start_date=est_time,
            end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC"))
        )
    assert "Datetime must be UTC" in str(exc_info.value)
