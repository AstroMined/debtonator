from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment, PaymentSource
from src.utils.datetime_utils import naive_utc_now, utc_now


@pytest_asyncio.fixture
async def test_payment(
    db_session: AsyncSession,
    test_checking_account,
    test_liability,
) -> Payment:
    """
    Create a test payment for use in tests.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture
        test_liability: Test liability fixture

    Returns:
        Payment: Created payment with associated payment source
    """
    # Create a naive datetime for DB storage
    payment_date = naive_utc_now()

    # Create payment model instance directly
    payment = Payment(
        amount=Decimal("50.00"),
        payment_date=payment_date,
        category="Utilities",
        description="Test payment for utilities",
        liability_id=test_liability.id,
    )

    # Add payment to session and flush to get ID
    db_session.add(payment)
    await db_session.flush()

    # Create payment source for the payment
    payment_source = PaymentSource(
        payment_id=payment.id,
        account_id=test_checking_account.id,
        amount=Decimal("50.00"),
    )

    # Add payment source to session
    db_session.add(payment_source)
    await db_session.flush()

    # Refresh payment to load relationship
    await db_session.refresh(payment)

    return payment


@pytest_asyncio.fixture
async def test_multiple_payments(
    db_session: AsyncSession,
    test_checking_account,
    test_second_checking_account,
    test_liability,
) -> List[Payment]:
    """
    Create multiple test payments with different dates and categories.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture
        test_second_checking_account: Test second account fixture
        test_liability: Test liability fixture

    Returns:
        List[Payment]: List of created payments with various configurations
    """
    now = utc_now()
    payment_data = [
        # Recent utility payment
        {
            "amount": Decimal("75.00"),
            "payment_date": now - timedelta(days=5),
            "category": "Utilities",
            "liability_id": test_liability.id,
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("75.00")}
            ],
        },
        # Older rent payment
        {
            "amount": Decimal("800.00"),
            "payment_date": now - timedelta(days=25),
            "category": "Rent",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("800.00")}
            ],
        },
        # Split payment for insurance
        {
            "amount": Decimal("120.00"),
            "payment_date": now - timedelta(days=10),
            "category": "Insurance",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("60.00")},
                {"account_id": test_second_checking_account.id, "amount": Decimal("60.00")},
            ],
        },
        # Future payment (scheduled)
        {
            "amount": Decimal("45.00"),
            "payment_date": now + timedelta(days=5),
            "category": "Subscription",
            "sources": [
                {"account_id": test_checking_account.id, "amount": Decimal("45.00")}
            ],
        },
    ]

    payments = []
    for data in payment_data:
        # Make datetime naive for DB storage
        naive_date = data["payment_date"].replace(tzinfo=None)

        # Create payment model instance directly
        payment = Payment(
            amount=data["amount"],
            payment_date=naive_date,
            category=data["category"],
            liability_id=data.get("liability_id"),
        )

        # Add payment to session and flush to get ID
        db_session.add(payment)
        await db_session.flush()

        # Create payment sources for the payment
        for source_data in data["sources"]:
            payment_source = PaymentSource(
                payment_id=payment.id,
                account_id=source_data["account_id"],
                amount=source_data["amount"],
            )
            db_session.add(payment_source)

        # Add to payments list
        payments.append(payment)

    # Flush to establish all database rows
    await db_session.flush()

    # Refresh all payments to load relationships
    for payment in payments:
        await db_session.refresh(payment)

    return payments


@pytest_asyncio.fixture
async def test_payment_source(
    db_session: AsyncSession,
    test_payment,
    test_checking_account,
) -> PaymentSource:
    """
    Create a test payment source.

    Note: This fixture creates a separate payment source, not directly
    associated with the test_payment fixture which already has its own source.
    """
    # Create model instance directly
    payment_source = PaymentSource(
        payment_id=test_payment.id,
        account_id=test_checking_account.id,
        amount=Decimal("75.00"),
    )

    # Add to session manually
    db_session.add(payment_source)
    await db_session.flush()
    await db_session.refresh(payment_source)

    return payment_source


@pytest_asyncio.fixture
async def test_payment_with_multiple_sources(
    db_session: AsyncSession,
    test_checking_account,
    test_second_checking_account,
) -> Payment:
    """
    Create a test payment with multiple payment sources.

    Args:
        db_session: Database session fixture
        test_checking_account: Test checking account fixture
        test_second_checking_account: Test second account fixture

    Returns:
        Payment: Created payment with multiple payment sources
    """
    # Create a naive datetime for DB storage
    payment_date = naive_utc_now()

    # Create payment model instance directly
    payment = Payment(
        amount=Decimal("150.00"),
        payment_date=payment_date,
        category="Bill Payment",
        description="Test payment with multiple sources",
    )

    # Add payment to session and flush to get ID
    db_session.add(payment)
    await db_session.flush()

    # Create payment sources
    sources = [
        PaymentSource(
            payment_id=payment.id,
            account_id=test_checking_account.id,
            amount=Decimal("100.00"),
        ),
        PaymentSource(
            payment_id=payment.id,
            account_id=test_second_checking_account.id,
            amount=Decimal("50.00"),
        ),
    ]

    # Add payment sources to session
    for source in sources:
        db_session.add(source)

    # Flush and refresh to establish relationships
    await db_session.flush()
    await db_session.refresh(payment)

    return payment
