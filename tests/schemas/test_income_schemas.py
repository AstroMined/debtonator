from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from pydantic import ValidationError

from src.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeFilters,
    RecurringIncomeCreate,
    RecurringIncomeUpdate
)

def test_income_create_with_utc_datetime():
    """Test creating an income record with UTC datetime"""
    income = IncomeCreate(
        date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
        source="Salary",
        amount=Decimal("5000.00"),
        account_id=1
    )
    assert income.date.tzinfo == ZoneInfo("UTC")

def test_income_create_rejects_naive_datetime():
    """Test that naive datetime is rejected"""
    with pytest.raises(ValidationError) as exc_info:
        IncomeCreate(
            date=datetime(2025, 3, 15),  # Naive datetime
            source="Salary",
            amount=Decimal("5000.00"),
            account_id=1
        )
    assert "Datetime must be UTC" in str(exc_info.value)

def test_income_create_rejects_non_utc_datetime():
    """Test that non-UTC datetime is rejected"""
    est_time = datetime(2025, 3, 15, tzinfo=ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError) as exc_info:
        IncomeCreate(
            date=est_time,
            source="Salary",
            amount=Decimal("5000.00"),
            account_id=1
        )
    assert "Datetime must be UTC" in str(exc_info.value)

def test_income_update_with_utc_datetime():
    """Test updating an income record with UTC datetime"""
    update = IncomeUpdate(
        date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
        amount=Decimal("5500.00")
    )
    assert update.date.tzinfo == ZoneInfo("UTC")

def test_income_update_optional_fields():
    """Test updating an income record with only some fields"""
    update = IncomeUpdate(amount=Decimal("5500.00"))
    assert update.amount == Decimal("5500.00")
    assert update.date is None
    assert update.source is None

def test_income_filters_with_utc_datetime():
    """Test income filters with UTC datetime"""
    filters = IncomeFilters(
        start_date=datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC")),
        end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC")),
        min_amount=Decimal("1000.00"),
        max_amount=Decimal("10000.00")
    )
    assert filters.start_date.tzinfo == ZoneInfo("UTC")
    assert filters.end_date.tzinfo == ZoneInfo("UTC")

def test_income_filters_rejects_naive_datetime():
    """Test that income filters reject naive datetime"""
    with pytest.raises(ValidationError) as exc_info:
        IncomeFilters(
            start_date=datetime(2025, 1, 1),  # Naive datetime
            end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC"))
        )
    assert "Datetime must be UTC" in str(exc_info.value)

def test_recurring_income_create_validation():
    """Test recurring income creation validation"""
    income = RecurringIncomeCreate(
        source="Monthly Salary",
        amount=Decimal("5000.00"),
        day_of_month=15,
        account_id=1
    )
    assert income.day_of_month == 15
    assert income.amount == Decimal("5000.00")

def test_recurring_income_create_invalid_day():
    """Test recurring income creation with invalid day"""
    with pytest.raises(ValidationError) as exc_info:
        RecurringIncomeCreate(
            source="Monthly Salary",
            amount=Decimal("5000.00"),
            day_of_month=32,  # Invalid day
            account_id=1
        )
    assert "Input should be less than or equal to 31" in str(exc_info.value)

def test_recurring_income_update_validation():
    """Test recurring income update validation"""
    update = RecurringIncomeUpdate(
        source="Updated Salary",
        day_of_month=20,
        active=True
    )
    assert update.day_of_month == 20
    assert update.active is True

def test_recurring_income_update_optional_fields():
    """Test recurring income update with optional fields"""
    update = RecurringIncomeUpdate(active=False)
    assert update.active is False
    assert update.source is None
    assert update.day_of_month is None
