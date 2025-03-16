from decimal import Decimal
from datetime import datetime
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
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
        test_checking_account: Account
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
                account_id=test_checking_account.id,
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

    async def test_payment_repr(self, db_session: AsyncSession, base_bill: Liability):
        """Test the string representation of Payment"""
        payment_date = naive_utc_from_date(2025, 2, 15)
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=payment_date,
            category="Utilities"
        )
        db_session.add(payment)
        await db_session.commit()
        
        expected_repr = f"<Payment {Decimal('100.00')} on {payment_date}>"
        assert repr(payment) == expected_repr

    async def test_payment_source_repr(
        self,
        db_session: AsyncSession,
        base_payment: Payment,
        test_checking_account: Account
    ):
        """Test the string representation of PaymentSource"""
        source = PaymentSource(
            payment_id=base_payment.id,
            account_id=test_checking_account.id,
            amount=Decimal("75.00")
        )
        db_session.add(source)
        await db_session.commit()
        
        expected_repr = f"<PaymentSource {Decimal('75.00')} from account {test_checking_account.id}>"
        assert repr(source) == expected_repr

    async def test_payment_with_description(self, db_session: AsyncSession, base_bill: Liability):
        """Test payment with description field"""
        payment = Payment(
            liability_id=base_bill.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Utilities",
            description="Test payment description"
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        
        assert payment.description == "Test payment description"

    async def test_payment_cascade_delete(
        self,
        db_session: AsyncSession,
        base_payment: Payment,
        test_checking_account: Account
    ):
        """Test cascading delete of payment sources when payment is deleted"""
        # Create additional payment source
        source = PaymentSource(
            payment_id=base_payment.id,
            account_id=test_checking_account.id,
            amount=Decimal("50.00")
        )
        db_session.add(source)
        await db_session.commit()
        
        # Verify sources exist
        await db_session.refresh(base_payment, ['sources'])
        assert len(base_payment.sources) > 0
        source_ids = [s.id for s in base_payment.sources]
        
        # Delete payment
        await db_session.delete(base_payment)
        await db_session.commit()
        
        # Verify sources were deleted
        for source_id in source_ids:
            result = await db_session.get(PaymentSource, source_id)
            assert result is None

    async def test_payment_with_income(
        self,
        db_session: AsyncSession,
        test_checking_account: Account
    ):
        """Test payment linked to income"""
        # Create income
        income = Income(
            date=naive_utc_from_date(2025, 2, 1),
            source="Test Income",
            amount=Decimal("1000.00"),
            deposited=True,
            account_id=test_checking_account.id
        )
        db_session.add(income)
        await db_session.commit()
        
        # Create payment linked to income
        payment = Payment(
            income_id=income.id,
            amount=Decimal("100.00"),
            payment_date=naive_utc_from_date(2025, 2, 15),
            category="Income Payment"
        )
        db_session.add(payment)
        await db_session.commit()
        
        # Test income relationship
        await db_session.refresh(payment, ['income'])
        assert payment.income_id == income.id
        assert payment.income.source == "Test Income"

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
