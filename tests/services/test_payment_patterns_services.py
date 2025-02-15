from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment, PaymentSource
from src.schemas.payment_patterns import PaymentPatternRequest, PatternType
from src.services.payment_patterns import PaymentPatternService


@pytest.fixture(scope="function")
def payment_pattern_service(db_session: AsyncSession):
    return PaymentPatternService(db_session)


@pytest.fixture(scope="function")
async def regular_payments(db_session: AsyncSession):
    """Create a set of regular monthly payments"""
    base_date = datetime(2024, 1, 1)
    payments = []
    
    for i in range(6):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=30 * i),
            category="utilities"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def irregular_payments(db_session: AsyncSession):
    """Create a set of irregular payments with varying amounts and dates"""
    base_date = datetime(2024, 1, 1)
    amounts = [Decimal('75.50'), Decimal('120.25'), Decimal('95.75'), Decimal('150.00')]
    days = [0, 15, 45, 90]  # Irregular intervals
    payments = []
    
    for amount, day in zip(amounts, days):
        payment = Payment(
            amount=amount,
            payment_date=base_date + timedelta(days=day),
            category="groceries"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def seasonal_payments(db_session: AsyncSession):
    """Create a set of monthly payments with seasonal variations"""
    base_date = datetime(2024, 1, 1)
    # Simulate higher amounts in summer months
    amounts = [
        Decimal('100.00'),  # January
        Decimal('100.00'),  # February
        Decimal('120.00'),  # March
        Decimal('150.00'),  # April
        Decimal('200.00'),  # May
        Decimal('250.00'),  # June
    ]
    payments = []
    
    for i, amount in enumerate(amounts):
        payment = Payment(
            amount=amount,
            payment_date=base_date + timedelta(days=30 * i),
            category="utilities"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


async def test_analyze_regular_pattern(
    payment_pattern_service: PaymentPatternService,
    regular_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.confidence_score >= 0.8
    assert analysis.sample_size == 6
    assert "consistent" in analysis.notes[0].lower()
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1
    assert analysis.amount_statistics.average_amount == Decimal('100.00')
    assert analysis.suggested_category == "utilities"


async def test_analyze_irregular_pattern(
    payment_pattern_service: PaymentPatternService,
    irregular_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="groceries"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.IRREGULAR
    assert analysis.confidence_score < 0.8
    assert analysis.sample_size == 4
    assert "irregular" in analysis.notes[0].lower()
    assert analysis.amount_statistics.min_amount == Decimal('75.50')
    assert analysis.amount_statistics.max_amount == Decimal('150.00')
    assert analysis.suggested_category == "groceries"


async def test_analyze_seasonal_pattern(
    payment_pattern_service: PaymentPatternService,
    seasonal_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.SEASONAL
    assert analysis.confidence_score > 0.5
    assert analysis.sample_size == 6
    assert any("seasonal" in note.lower() or "monthly" in note.lower() for note in analysis.notes)
    assert analysis.amount_statistics.min_amount == Decimal('100.00')
    assert analysis.amount_statistics.max_amount == Decimal('250.00')
    assert analysis.suggested_category == "utilities"


async def test_insufficient_data_pattern(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    # Create just one payment (below min_sample_size)
    payment = Payment(
        amount=Decimal('100.00'),
        payment_date=datetime(2024, 1, 1),
        category="misc"
    )
    db_session.add(payment)
    # Add payment source
    source = PaymentSource(
        payment=payment,
        account_id=1,
        amount=Decimal('100.00')
    )
    db_session.add(source)
    await db_session.commit()
    
    request = PaymentPatternRequest(
        account_id=1,
        category_id="misc",
        min_sample_size=3  # Require at least 3 samples
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.UNKNOWN
    assert analysis.confidence_score == 0.0
    assert analysis.sample_size == 1
    assert "insufficient data" in analysis.notes[0].lower()


async def test_date_range_filter(
    payment_pattern_service: PaymentPatternService,
    regular_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        start_date=datetime(2024, 2, 1),
        end_date=datetime(2024, 4, 1)
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.sample_size < 6  # Should only include payments within date range
    assert analysis.analysis_period_start >= datetime(2024, 2, 1)
    assert analysis.analysis_period_end <= datetime(2024, 4, 1)
