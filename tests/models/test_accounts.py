from decimal import Decimal
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account

pytestmark = pytest.mark.asyncio

class TestAccount:
    async def test_create_checking_account(self, db_session: AsyncSession):
        """Test creating a checking account"""
        account = Account(
            name="Basic Checking Account",
            type="checking",
            available_balance=Decimal("1000.00"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.id is not None
        assert account.name == "Basic Checking Account"
        assert account.type == "checking"
        assert account.available_balance == Decimal("1000.00")
        assert account.available_credit is None
        assert account.total_limit is None

    async def test_create_credit_account(self, db_session: AsyncSession):
        """Test creating a credit account with limit"""
        # Create account first with type and limit
        account = Account(
            name="Basic Credit Card",
            type="credit",
            total_limit=Decimal("2000.00"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(account)
        await db_session.commit()
        
        # Then set the balance which will trigger available_credit calculation
        account.available_balance = Decimal("-500.00")
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.id is not None
        assert account.name == "Basic Credit Card"
        assert account.type == "credit"
        assert account.available_balance == Decimal("-500.00")
        assert account.total_limit == Decimal("2000.00")
        # Available credit should be total_limit minus the absolute value of the balance
        assert account.available_credit == Decimal("1500.00")

    async def test_create_savings_account(self, db_session: AsyncSession):
        """Test creating a savings account"""
        account = Account(
            name="Basic Savings Account",
            type="savings",
            available_balance=Decimal("5000.00"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        assert account.id is not None
        assert account.name == "Basic Savings Account"
        assert account.type == "savings"
        assert account.available_balance == Decimal("5000.00")
        assert account.available_credit is None
        assert account.total_limit is None

    async def test_update_account_balance(self, db_session: AsyncSession, base_account: Account):
        """Test updating an account's balance"""
        # Add $500 to the balance
        base_account.available_balance += Decimal("500.00")
        await db_session.commit()
        await db_session.refresh(base_account)

        assert base_account.available_balance == Decimal("1500.00")

    async def test_credit_account_available_credit(self, db_session: AsyncSession):
        """Test available credit calculation for credit accounts"""
        account = Account(
            name="Available Credit Test Card",
            type="credit",
            total_limit=Decimal("1000.00"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(account)
        await db_session.commit()

        # Set initial balance
        account.available_balance = Decimal("0.00")
        db_session.add(account)
        await db_session.commit()

        # Initial state - no balance used
        assert account.available_credit == Decimal("1000.00")

        # Use some credit
        account.available_balance = Decimal("-300.00")
        await db_session.commit()
        await db_session.refresh(account)

        # Available credit should be reduced
        assert account.available_credit == Decimal("700.00")

        # Use all credit
        account.available_balance = Decimal("-1000.00")
        await db_session.commit()
        await db_session.refresh(account)

        # No credit should be available
        assert account.available_credit == Decimal("0.00")
