import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.accounts import Account

@pytest.fixture
async def sample_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def sample_liability(db_session: AsyncSession) -> Liability:
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=date(2025, 1, 1),
        category="Utilities",
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 1}
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)
    return liability

@pytest.mark.asyncio
async def test_liability_creation(db_session: AsyncSession, sample_liability: Liability):
    """Test creating a new liability"""
    retrieved = await db_session.get(Liability, sample_liability.id)
    assert retrieved is not None
    assert retrieved.name == "Test Bill"
    assert retrieved.amount == Decimal("100.00")
    assert retrieved.category == "Utilities"
    assert retrieved.recurring is True
    assert retrieved.recurrence_pattern == {"frequency": "monthly", "day": 1}

@pytest.mark.asyncio
async def test_payment_with_source(
    db_session: AsyncSession,
    sample_liability: Liability,
    sample_account: Account
):
    """Test creating a payment with a payment source"""
    # Create payment
    payment = Payment(
        liability_id=sample_liability.id,
        amount=Decimal("100.00"),
        payment_date=date(2025, 1, 1),
        category="Utilities"
    )
    db_session.add(payment)
    await db_session.flush()

    # Create payment source
    source = PaymentSource(
        payment_id=payment.id,
        account_id=sample_account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    await db_session.commit()

    # Verify relationships
    await db_session.refresh(payment)
    assert len(payment.sources) == 1
    assert payment.sources[0].amount == Decimal("100.00")
    assert payment.sources[0].account_id == sample_account.id

    # Verify liability relationship
    await db_session.refresh(sample_liability)
    assert len(sample_liability.payments) == 1
    assert sample_liability.payments[0].id == payment.id

@pytest.mark.asyncio
async def test_split_payment(
    db_session: AsyncSession,
    sample_liability: Liability,
    sample_account: Account
):
    """Test creating a split payment across multiple accounts"""
    # Create second account
    account2 = Account(
        name="Second Account",
        type="credit",
        available_balance=Decimal("500.00")
    )
    db_session.add(account2)
    await db_session.flush()

    # Create payment
    payment = Payment(
        liability_id=sample_liability.id,
        amount=Decimal("100.00"),
        payment_date=date(2025, 1, 1),
        category="Utilities"
    )
    db_session.add(payment)
    await db_session.flush()

    # Create split payment sources
    source1 = PaymentSource(
        payment_id=payment.id,
        account_id=sample_account.id,
        amount=Decimal("60.00")
    )
    source2 = PaymentSource(
        payment_id=payment.id,
        account_id=account2.id,
        amount=Decimal("40.00")
    )
    db_session.add_all([source1, source2])
    await db_session.commit()

    # Verify payment sources
    await db_session.refresh(payment)
    assert len(payment.sources) == 2
    total_amount = sum(source.amount for source in payment.sources)
    assert total_amount == payment.amount

@pytest.mark.asyncio
async def test_cascade_delete_payment(
    db_session: AsyncSession,
    sample_liability: Liability,
    sample_account: Account
):
    """Test that deleting a payment cascades to payment sources"""
    # Create payment with source
    payment = Payment(
        liability_id=sample_liability.id,
        amount=Decimal("100.00"),
        payment_date=date(2025, 1, 1),
        category="Utilities"
    )
    db_session.add(payment)
    await db_session.flush()

    source = PaymentSource(
        payment_id=payment.id,
        account_id=sample_account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    await db_session.commit()

    # Delete payment
    await db_session.delete(payment)
    await db_session.commit()

    # Verify payment source is also deleted
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM payment_sources WHERE payment_id = :pid"),
        {"pid": payment.id}
    )
    count = result.scalar()
    assert count == 0

@pytest.mark.asyncio
async def test_cascade_delete_liability(
    db_session: AsyncSession,
    sample_liability: Liability,
    sample_account: Account
):
    """Test that deleting a liability cascades to payments and sources"""
    # Create payment with source
    payment = Payment(
        liability_id=sample_liability.id,
        amount=Decimal("100.00"),
        payment_date=date(2025, 1, 1),
        category="Utilities"
    )
    db_session.add(payment)
    await db_session.flush()

    source = PaymentSource(
        payment_id=payment.id,
        account_id=sample_account.id,
        amount=Decimal("100.00")
    )
    db_session.add(source)
    await db_session.commit()

    # Delete liability
    await db_session.delete(sample_liability)
    await db_session.commit()

    # Verify payment and source are deleted
    payment_result = await db_session.execute(
        text("SELECT COUNT(*) FROM payments WHERE liability_id = :lid"),
        {"lid": sample_liability.id}
    )
    source_result = await db_session.execute(
        text("SELECT COUNT(*) FROM payment_sources WHERE payment_id = :pid"),
        {"pid": payment.id}
    )
    assert payment_result.scalar() == 0
    assert source_result.scalar() == 0
