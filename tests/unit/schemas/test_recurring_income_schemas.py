from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.recurring_income import RecurringIncomeCreate, RecurringIncomeUpdate


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

    def test_update_schema(self):
        """Test the RecurringIncomeUpdate schema"""
        # Test partial update (only some fields)
        update = RecurringIncomeUpdate(
            source="Updated Salary",
            amount=Decimal("6000.00"),
        )
        assert update.source == "Updated Salary"
        assert update.amount == Decimal("6000.00")
        assert update.day_of_month is None
        assert update.account_id is None
        assert update.auto_deposit is None
        assert update.active is None

        # Test full update
        full_update = RecurringIncomeUpdate(
            source="Full Update",
            amount=Decimal("7000.00"),
            day_of_month=20,
            account_id=2,
            auto_deposit=True,
            active=False,
        )
        assert full_update.source == "Full Update"
        assert full_update.amount == Decimal("7000.00")
        assert full_update.day_of_month == 20
        assert full_update.account_id == 2
        assert full_update.auto_deposit is True
        assert full_update.active is False
