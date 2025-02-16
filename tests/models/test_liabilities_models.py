from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.categories import Category

pytestmark = pytest.mark.asyncio

class TestLiability:
    async def test_create_basic_liability(self, db_session: AsyncSession, base_account: Account):
        """Test creating a basic liability (bill)"""
        # Create category first
        utilities_category = Category(name="Utilities")
        db_session.add(utilities_category)
        await db_session.commit()

        liability = Liability(
            name="Internet Bill",
            amount=Decimal("89.99"),
            due_date=datetime(2025, 3, 15),
            category_id=utilities_category.id,
            recurring=False,
            primary_account_id=base_account.id,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC"))
        )
        db_session.add(liability)
        await db_session.commit()
        await db_session.refresh(liability)

        assert liability.id is not None
        assert liability.name == "Internet Bill"
        assert liability.amount == Decimal("89.99")
        assert liability.due_date == datetime(2025, 3, 15)
        assert liability.category.name == "Utilities"
        assert liability.recurring is False
        assert liability.primary_account_id == base_account.id
        assert liability.paid is False
        assert liability.auto_pay is False

    async def test_create_recurring_liability(self, db_session: AsyncSession, base_account: Account):
        """Test creating a recurring liability"""
        # Create category first
        entertainment_category = Category(name="Entertainment")
        db_session.add(entertainment_category)
        await db_session.commit()

        liability = Liability(
            name="Netflix Subscription",
            amount=Decimal("19.99"),
            due_date=datetime(2025, 3, 1),
            category_id=entertainment_category.id,
            recurring=True,
            recurrence_pattern={"frequency": "monthly", "day": 1},
            primary_account_id=base_account.id,
            auto_pay=True,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC"))
        )
        db_session.add(liability)
        await db_session.commit()
        await db_session.refresh(liability)

        assert liability.id is not None
        assert liability.name == "Netflix Subscription"
        assert liability.amount == Decimal("19.99")
        assert liability.recurring is True
        assert liability.recurrence_pattern == {"frequency": "monthly", "day": 1}
        assert liability.auto_pay is True

    async def test_update_liability_amount(self, db_session: AsyncSession, base_bill: Liability):
        """Test updating a liability's amount"""
        # Update the amount
        base_bill.amount = Decimal("150.00")
        await db_session.commit()
        await db_session.refresh(base_bill)

        assert base_bill.amount == Decimal("150.00")

    async def test_liability_with_description(self, db_session: AsyncSession, base_account: Account):
        """Test creating a liability with an optional description"""
        # Create category first
        insurance_category = Category(name="Insurance")
        db_session.add(insurance_category)
        await db_session.commit()

        liability = Liability(
            name="Car Insurance",
            amount=Decimal("200.00"),
            due_date=datetime(2025, 3, 1),
            category_id=insurance_category.id,
            description="Semi-annual premium payment",
            recurring=False,
            primary_account_id=base_account.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(liability)
        await db_session.commit()
        await db_session.refresh(liability)

        assert liability.description == "Semi-annual premium payment"

    async def test_mark_liability_as_paid(self, db_session: AsyncSession, base_bill: Liability):
        """Test marking a liability as paid"""
        base_bill.paid = True
        await db_session.commit()
        await db_session.refresh(base_bill)

        assert base_bill.paid is True

    async def test_liability_account_relationship(self, db_session: AsyncSession, base_bill: Liability):
        """Test the relationship between liability and account"""
        assert base_bill.primary_account is not None
        assert "Primary Test Checking" in base_bill.primary_account.name

    async def test_liability_defaults(self, db_session: AsyncSession, base_account: Account):
        """Test liability creation with minimal required fields"""
        # Create category first
        other_category = Category(name="Other")
        db_session.add(other_category)
        await db_session.commit()

        liability = Liability(
            name="Simple Bill",
            amount=Decimal("50.00"),
            due_date=datetime(2025, 3, 1),
            category_id=other_category.id,
            primary_account_id=base_account.id
        )
        db_session.add(liability)
        await db_session.commit()
        await db_session.refresh(liability)

        assert liability.id is not None
        assert liability.recurring is False
        assert liability.description is None
        assert liability.recurrence_pattern is None
        assert liability.auto_pay is False
        assert liability.paid is False
        assert isinstance(liability.created_at, datetime)
        assert isinstance(liability.updated_at, datetime)
