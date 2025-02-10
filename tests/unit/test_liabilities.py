from datetime import date, datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError

from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource

def test_create_liability(db_session):
    """Test creating a basic liability"""
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=date.today(),
        category="Utilities",
        description="Test description"
    )
    db_session.add(liability)
    db_session.commit()

    assert liability.id is not None
    assert liability.name == "Test Bill"
    assert liability.amount == Decimal("100.00")
    assert liability.due_date == date.today()
    assert liability.category == "Utilities"
    assert liability.description == "Test description"
    assert liability.recurring is False
    assert liability.recurrence_pattern is None
    assert isinstance(liability.created_at, datetime)
    assert isinstance(liability.updated_at, datetime)

def test_create_recurring_liability(db_session):
    """Test creating a recurring liability with pattern"""
    recurrence_pattern = {
        "frequency": "monthly",
        "day_of_month": 15,
        "end_date": (date.today() + timedelta(days=365)).isoformat()
    }
    
    liability = Liability(
        name="Recurring Bill",
        amount=Decimal("50.00"),
        due_date=date.today(),
        category="Subscription",
        recurring=True,
        recurrence_pattern=recurrence_pattern
    )
    db_session.add(liability)
    db_session.commit()

    assert liability.recurring is True
    assert liability.recurrence_pattern == recurrence_pattern

def test_liability_required_fields(db_session):
    """Test that required fields raise appropriate errors when missing"""
    liability = Liability()
    db_session.add(liability)
    
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_liability_payment_relationship(db_session):
    """Test the relationship between liability and payments"""
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

    assert len(liability.payments) == 1
    assert liability.payments[0].amount == Decimal("100.00")

def test_liability_cascade_delete(db_session):
    """Test that deleting a liability cascades to related payments"""
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

    db_session.delete(liability)
    db_session.commit()

    # Verify payment was deleted
    assert db_session.query(Payment).filter_by(bill_id=liability.id).first() is None
