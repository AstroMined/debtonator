from datetime import date, datetime
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError

from src.models.payments import Payment, PaymentSource
from src.models.liabilities import Liability
from src.models.accounts import Account

def test_create_payment(db_session):
    """Test creating a basic payment without a bill"""
    payment = Payment(
        amount=Decimal("50.00"),
        payment_date=date.today(),
        category="Groceries",
        description="Weekly groceries"
    )
    db_session.add(payment)
    db_session.commit()

    assert payment.id is not None
    assert payment.bill_id is None
    assert payment.amount == Decimal("50.00")
    assert payment.payment_date == date.today()
    assert payment.category == "Groceries"
    assert payment.description == "Weekly groceries"
    assert isinstance(payment.created_at, datetime)
    assert isinstance(payment.updated_at, datetime)

def test_create_bill_payment(db_session):
    """Test creating a payment linked to a bill"""
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=date.today(),
        category="Utilities"
    )
    db_session.add(liability)
    db_session.commit()

    payment = Payment(
        bill_id=liability.id,
        amount=Decimal("100.00"),
        payment_date=date.today(),
        category="Utilities"
    )
    db_session.add(payment)
    db_session.commit()

    assert payment.bill_id == liability.id
    assert payment.bill.name == "Test Bill"

def test_payment_required_fields(db_session):
    """Test that required fields raise appropriate errors when missing"""
    payment = Payment()
    db_session.add(payment)
    
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_create_payment_source(db_session):
    """Test creating a payment source"""
    # Create account
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    
    # Create payment
    payment = Payment(
        amount=Decimal("100.00"),
        payment_date=date.today(),
        category="Utilities"
    )
    db_session.add(payment)
    db_session.commit()

    # Create payment source
    source = PaymentSource(
        payment_id=payment.id,
        account_id=account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    db_session.commit()

    assert source.id is not None
    assert source.payment_id == payment.id
    assert source.account_id == account.id
    assert source.amount == Decimal("100.00")
    assert isinstance(source.created_at, datetime)
    assert isinstance(source.updated_at, datetime)

def test_payment_sources_relationship(db_session):
    """Test the relationship between payment and its sources"""
    # Create accounts
    account1 = Account(name="Account 1", type="checking")
    account2 = Account(name="Account 2", type="savings")
    db_session.add_all([account1, account2])
    
    # Create payment
    payment = Payment(
        amount=Decimal("100.00"),
        payment_date=date.today(),
        category="Utilities"
    )
    db_session.add(payment)
    db_session.commit()

    # Create split payment sources
    source1 = PaymentSource(
        payment_id=payment.id,
        account_id=account1.id,
        amount=Decimal("60.00")
    )
    source2 = PaymentSource(
        payment_id=payment.id,
        account_id=account2.id,
        amount=Decimal("40.00")
    )
    db_session.add_all([source1, source2])
    db_session.commit()

    assert len(payment.sources) == 2
    assert sum(source.amount for source in payment.sources) == payment.amount

def test_payment_cascade_delete(db_session):
    """Test that deleting a payment cascades to payment sources"""
    # Create account and payment
    account = Account(name="Test Account", type="checking")
    db_session.add(account)
    
    payment = Payment(
        amount=Decimal("100.00"),
        payment_date=date.today(),
        category="Utilities"
    )
    db_session.add(payment)
    db_session.commit()

    # Create payment source
    source = PaymentSource(
        payment_id=payment.id,
        account_id=account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    db_session.commit()

    # Delete payment and verify cascade
    db_session.delete(payment)
    db_session.commit()

    assert db_session.query(PaymentSource).filter_by(payment_id=payment.id).first() is None

def test_payment_source_account_relationship(db_session):
    """Test the relationship between payment source and account"""
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    
    payment = Payment(
        amount=Decimal("100.00"),
        payment_date=date.today(),
        category="Utilities"
    )
    db_session.add(payment)
    db_session.commit()

    source = PaymentSource(
        payment_id=payment.id,
        account_id=account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    db_session.commit()

    assert source.account.name == "Test Account"
    assert source in account.payment_sources
