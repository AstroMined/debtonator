from decimal import Decimal
from datetime import datetime
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.base_model import naive_utc_now, naive_utc_from_date

pytestmark = pytest.mark.asyncio

class TestPayment:
    async def test_create_payment(self, db_session: AsyncSession, base_bill: Liability):
        """Test creating a basic payment"""
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Utilities",
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)

        assert payment.id is not None
        assert payment.liability_id == base_bill.id
        assert payment.amount == Decimal("100.00")
        # Compare date components since SQLite might not preserve timezone info
        assert payment.payment_date.year == 2025
        assert payment.payment_date.month == 2
        assert payment.payment_date.day == 15
        assert payment.category == "Utilities"

    async def test_payment_with_source(self, db_session: AsyncSession, base_payment: Payment):
        """Test payment with associated payment source"""
        # Load the relationship
        await db_session.refresh(base_payment, ['sources'])
        
        assert len(base_payment.sources) == 1
        payment_source = base_payment.sources[0]
        assert payment_source.payment_id == base_payment.id
        assert payment_source.amount == base_payment.amount

    async def test_create_split_payment(
        self, 
        db_session: AsyncSession, 
        base_bill: Liability, 
        base_account: Account
    ):
        """Test creating a payment split across multiple sources"""
        # Create another account for split
        second_account = Account(
            name="Split Payment Test Account",
            type="savings",
            available_balance=Decimal("2000.00"),
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
        )
        db_session.add(second_account)
        await db_session.commit()

        # Create payment
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Utilities",
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)

        # Create split payment sources
        sources = [
            PaymentSource(
                payment_id=payment.id,
                account_id=base_account.id,
                amount=Decimal("60.00"),
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
            ),
            PaymentSource(
                payment_id=payment.id,
                account_id=second_account.id,
                amount=Decimal("40.00"),
                created_at=naive_utc_now(),
                updated_at=naive_utc_now()
            )
        ]
        db_session.add_all(sources)
        await db_session.commit()
        await db_session.refresh(payment)

        # Load relationships
        await db_session.refresh(payment, ['sources'])
        assert len(payment.sources) == 2
        
        # Calculate total from sources
        total_source_amount = sum(source.amount for source in payment.sources)
        assert total_source_amount == payment.amount

    async def test_payment_liability_relationship(self, db_session: AsyncSession, base_payment: Payment):
        """Test the relationship between payment and liability"""
        # Load the relationship
        await db_session.refresh(base_payment, ['liability'])
        
        assert base_payment.liability is not None
        assert "Test Bill" in base_payment.liability.name

    async def test_payment_source_account_relationship(
        self, 
        db_session: AsyncSession, 
        base_payment: Payment
    ):
        """Test the relationship between payment source and account"""
        # Load the relationships
        await db_session.refresh(base_payment, ['sources'])
        source = base_payment.sources[0]
        await db_session.refresh(source, ['account'])
        
        assert source.account is not None
        assert "Primary Test Checking" in source.account.name

    async def test_payment_defaults(self, db_session: AsyncSession, base_bill: Liability):
        """Test payment creation with minimal required fields"""
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Utilities"
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)

        assert payment.id is not None
        assert isinstance(payment.created_at, datetime)
        assert isinstance(payment.updated_at, datetime)
        
        # Load relationships
        await db_session.refresh(payment, ['sources'])
        assert len(payment.sources) == 0

    async def test_datetime_handling(self, db_session: AsyncSession, base_bill: Liability):
        """Test proper datetime handling in payments"""
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Utilities",
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)

        # Verify all datetime fields are naive (no tzinfo)
        assert payment.payment_date.tzinfo is None
        assert payment.created_at.tzinfo is None
        assert payment.updated_at.tzinfo is None

        # Verify payment_date components
        assert payment.payment_date.year == 2025
        assert payment.payment_date.month == 2
        assert payment.payment_date.day == 15
        assert payment.payment_date.hour == 0
        assert payment.payment_date.minute == 0
        assert payment.payment_date.second == 0

        # Test payment source datetime handling
        source = PaymentSource(
            payment_id=payment.id,
            account_id=base_bill.primary_account_id,
            amount=Decimal("100.00"),
            created_at=naive_utc_now(),
            updated_at=naive_utc_now()
        )
        db_session.add(source)
        await db_session.commit()
        await db_session.refresh(source)

        # Verify source datetime fields are naive
        assert source.created_at.tzinfo is None
        assert source.updated_at.tzinfo is None
