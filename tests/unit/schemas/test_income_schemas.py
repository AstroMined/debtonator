from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from src.schemas.income import (
    IncomeCreate,
    IncomeFilters,
    IncomeUpdate,
    RecurringIncomeCreate,
    RecurringIncomeUpdate,
)


class TestIncomeCreate:
    """Test cases for IncomeCreate schema"""

    def test_valid_income_create(self):
        """Test creating a valid income record"""
        income = IncomeCreate(
            date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
            source="Salary",
            amount=Decimal("5000.00"),
            account_id=1,
        )
        assert income.date.tzinfo == ZoneInfo("UTC")
        assert income.amount == Decimal("5000.00")
        assert income.source == "Salary"
        assert income.account_id == 1
        assert income.deposited is False

    def test_rejects_naive_datetime(self):
        """Test that naive datetime is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=datetime(2025, 3, 15),  # Naive datetime
                source="Salary",
                amount=Decimal("5000.00"),
                account_id=1,
            )
        assert "Datetime must be UTC" in str(exc_info.value)

    def test_rejects_non_utc_datetime(self):
        """Test that non-UTC datetime is rejected"""
        est_time = datetime(2025, 3, 15, tzinfo=ZoneInfo("America/New_York"))
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=est_time, source="Salary", amount=Decimal("5000.00"), account_id=1
            )
        assert "Datetime must be UTC" in str(exc_info.value)

    def test_amount_validation(self):
        """Test amount validation rules"""
        # Test invalid decimal places
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
                source="Salary",
                amount=Decimal("5000.001"),  # Three decimal places
                account_id=1,
            )
        assert "Input should be a multiple of 0.01" in str(exc_info.value)

        # Test zero amount
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
                source="Salary",
                amount=Decimal("0.00"),
                account_id=1,
            )
        assert "Input should be greater than or equal to 0.01" in str(exc_info.value)

    def test_source_validation(self):
        """Test source field validation"""
        # Test empty source
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
                source="",  # Empty string
                amount=Decimal("5000.00"),
                account_id=1,
            )
        assert "String should have at least 1 character" in str(exc_info.value)

        # Test too long source
        with pytest.raises(ValidationError) as exc_info:
            IncomeCreate(
                date=datetime(2025, 3, 15, tzinfo=ZoneInfo("UTC")),
                source="x" * 256,  # 256 characters
                amount=Decimal("5000.00"),
                account_id=1,
            )
        assert "String should have at most 255 characters" in str(exc_info.value)


class TestRecurringIncome:
    """Test cases for RecurringIncome schemas"""

    def test_valid_recurring_income(self):
        """Test creating a valid recurring income"""
        income = RecurringIncomeCreate(
            source="Monthly Salary",
            amount=Decimal("5000.00"),
            day_of_month=15,
            account_id=1,
        )
        assert income.day_of_month == 15
        assert income.amount == Decimal("5000.00")
        assert income.auto_deposit is False

    def test_rejects_day_31(self):
        """Test that day 31 is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RecurringIncomeCreate(
                source="Monthly Salary",
                amount=Decimal("5000.00"),
                day_of_month=31,
                account_id=1,
            )
        assert "Day 31 is not supported" in str(exc_info.value)

    def test_amount_precision(self):
        """Test amount precision validation"""
        with pytest.raises(ValidationError) as exc_info:
            RecurringIncomeCreate(
                source="Monthly Salary",
                amount=Decimal("5000.001"),  # Three decimal places
                day_of_month=15,
                account_id=1,
            )
        assert "Input should be a multiple of 0.01" in str(exc_info.value)


class TestIncomeFilters:
    """Test cases for IncomeFilters schema"""

    def test_valid_filters(self):
        """Test valid filter combinations"""
        filters = IncomeFilters(
            start_date=datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC")),
            end_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC")),
            min_amount=Decimal("1000.00"),
            max_amount=Decimal("10000.00"),
        )
        assert filters.start_date.tzinfo == ZoneInfo("UTC")
        assert filters.end_date.tzinfo == ZoneInfo("UTC")
        assert filters.min_amount == Decimal("1000.00")
        assert filters.max_amount == Decimal("10000.00")

    def test_invalid_date_range(self):
        """Test invalid date range validation"""
        with pytest.raises(ValidationError) as exc_info:
            IncomeFilters(
                start_date=datetime(2025, 12, 31, tzinfo=ZoneInfo("UTC")),
                end_date=datetime(2025, 1, 1, tzinfo=ZoneInfo("UTC")),
            )
        assert "end_date must be after start_date" in str(exc_info.value)

    def test_invalid_amount_range(self):
        """Test invalid amount range validation"""
        with pytest.raises(ValidationError) as exc_info:
            IncomeFilters(min_amount=Decimal("5000.00"), max_amount=Decimal("1000.00"))
        assert "max_amount must be greater than min_amount" in str(exc_info.value)

    def test_amount_precision(self):
        """Test amount precision validation in filters"""
        with pytest.raises(ValidationError) as exc_info:
            IncomeFilters(
                min_amount=Decimal("1000.001"),  # Three decimal places
                max_amount=Decimal("2000.001"),  # Three decimal places
            )
        assert "Input should be a multiple of 0.01" in str(exc_info.value)
