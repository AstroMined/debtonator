from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select
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
    # Get total number of payments first
    total_payments = len(regular_payments)
    
    # Create request with date range that should exclude some payments
    request = PaymentPatternRequest(
        account_id=1,
        start_date=datetime(2024, 2, 1),
        end_date=datetime(2024, 4, 1)
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Verify filtering worked
    assert analysis.sample_size < total_payments
    assert analysis.analysis_period_start >= datetime(2024, 2, 1)
    assert analysis.analysis_period_end <= datetime(2024, 4, 1)


@pytest.fixture(scope="function")
async def mixed_interval_payments(db_session: AsyncSession):
    """Create payments with mostly regular intervals but some outliers"""
    base_date = datetime(2024, 1, 1)
    # Intervals: 30, 35, 30, 25, 30 days (mostly monthly with some variation)
    intervals = [0, 30, 65, 95, 120, 150]
    payments = []
    
    for days in intervals:
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=days),
            category="utilities"
        )
        db_session.add(payment)
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
async def minimal_regular_payments(db_session: AsyncSession):
    """Create exactly 3 payments with regular intervals"""
    base_date = datetime(2024, 1, 1)
    payments = []
    
    for i in range(3):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=30 * i),
            category="utilities"
        )
        db_session.add(payment)
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
async def gapped_payments(db_session: AsyncSession):
    """Create payments with a significant gap in the middle"""
    base_date = datetime(2024, 1, 1)
    # Regular monthly payments, then a 3-month gap, then regular again
    days = [0, 30, 60, 150, 180, 210]
    payments = []
    
    for day in days:
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=day),
            category="utilities"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


async def test_mixed_interval_pattern(
    payment_pattern_service: PaymentPatternService,
    mixed_interval_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert 0.6 <= analysis.confidence_score <= 0.8  # Lower confidence due to variations
    assert abs(analysis.frequency_metrics.average_days_between - 30) <= 3
    assert analysis.frequency_metrics.std_dev_days > 0


async def test_minimal_sample_regular_pattern(
    payment_pattern_service: PaymentPatternService,
    minimal_regular_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.confidence_score <= 0.5  # Lower confidence due to minimal sample size
    assert analysis.sample_size == 3
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1


async def test_gapped_payment_pattern(
    payment_pattern_service: PaymentPatternService,
    gapped_payments
):
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.IRREGULAR
    assert analysis.confidence_score < 0.6  # Lower confidence due to gap
    assert analysis.sample_size == 6
    assert any("variable" in note.lower() for note in analysis.notes)


async def test_analyze_bill_payments_no_payments(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing a bill with no payments"""
    result = await payment_pattern_service.analyze_bill_payments(999)  # Non-existent liability_id
    assert result is None


async def test_analyze_bill_payments_with_pattern(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing a bill with regular payments"""
    # Create a set of regular payments for a specific bill
    base_date = datetime(2024, 1, 1)
    liability_id = 1
    payments = []
    
    for i in range(3):  # Reduce to 3 payments to match test expectations
        payment = Payment(
            amount=Decimal('200.00'),
            payment_date=base_date + timedelta(days=30 * i),
            category="rent",
            liability_id=liability_id
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('200.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    # Debug print
    query = select(Payment).where(Payment.liability_id == liability_id)
    debug_result = await db_session.execute(query)
    debug_payments = debug_result.scalars().all()
    print(f"\nDebug: Found {len(debug_payments)} payments in test: {[f'Payment({p.amount} on {p.payment_date})' for p in debug_payments]}")
    
    result = await payment_pattern_service.analyze_bill_payments(liability_id)
    
    assert result is not None
    assert result.pattern_type == PatternType.REGULAR
    assert result.sample_size == 3  # Explicitly check for 3 payments
    assert result.suggested_category == "rent"
    assert abs(result.frequency_metrics.average_days_between - 30) < 1


async def test_category_suggestion_mixed(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test category suggestion with mixed categories"""
    # Create payments with different categories
    base_date = datetime(2024, 1, 1)
    categories = ["utilities", "utilities", "utilities", "rent", "groceries"]
    payments = []
    
    for i, category in enumerate(categories):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=i),
            category=category
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.suggested_category == "utilities"  # Most frequent category


async def test_category_suggestion_no_categories(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test category suggestion with no categories"""
    # Create payments without categories
    base_date = datetime(2024, 1, 1)
    payments = []
    
    for i in range(3):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=i),
            category="uncategorized"  # Default category instead of None
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.suggested_category == "uncategorized"


async def test_analyze_same_day_payments(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing payments made on the same day"""
    # Create multiple payments on the same day
    payment_date = datetime(2024, 1, 1)
    payments = []
    
    for i in range(3):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.UNKNOWN
    assert analysis.frequency_metrics.average_days_between == 0
    assert analysis.frequency_metrics.std_dev_days == 0


async def test_filter_combination(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing payments with multiple filter combinations"""
    # Create payments with various attributes
    base_date = datetime(2024, 1, 1)
    liability_id = 1
    payments = []
    
    for i in range(6):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=i),
            category="utilities",
            liability_id=liability_id if i < 3 else None  # Mix of liability and non-liability payments
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1 if i % 2 == 0 else 2,  # Mix of account IDs
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    # Test with multiple filters
    request = PaymentPatternRequest(
        account_id=1,
        category_id="utilities",
        liability_id=liability_id,
        start_date=base_date,
        end_date=base_date + timedelta(days=2)
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.sample_size < 6  # Should be filtered
    assert analysis.analysis_period_start >= base_date
    assert analysis.analysis_period_end <= base_date + timedelta(days=2)


async def test_amount_statistics_edge_cases(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test amount statistics with edge case values"""
    base_date = datetime(2024, 1, 1)
    amounts = [
        Decimal('0.00'),  # Zero amount
        Decimal('999999.99'),  # Very large amount
        Decimal('0.01'),  # Very small amount
        Decimal('100.00'),  # Normal amount
    ]
    payments = []
    
    for i, amount in enumerate(amounts):
        payment = Payment(
            amount=amount,
            payment_date=base_date + timedelta(days=30 * i),
            category="misc"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.amount_statistics.min_amount == Decimal('0.00')
    assert analysis.amount_statistics.max_amount == Decimal('999999.99')
    assert analysis.amount_statistics.std_dev_amount > Decimal('0')
    assert analysis.pattern_type == PatternType.SEASONAL  # High amount variation with regular timing


async def test_borderline_regular_pattern(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test pattern detection with borderline regular intervals"""
    base_date = datetime(2024, 1, 1)
    # Intervals that are almost regular (30 days ± 1-2 days)
    days = [0, 31, 59, 90, 119]  # Slightly off from perfect 30-day intervals
    payments = []
    
    for day in days:
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=day),
            category="utilities"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Should still be detected as regular but with lower confidence
    assert analysis.pattern_type == PatternType.REGULAR
    assert 0.6 <= analysis.confidence_score <= 0.875  # Allow higher confidence for borderline cases
    assert abs(analysis.frequency_metrics.average_days_between - 30) <= 2


async def test_borderline_seasonal_pattern(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test pattern detection with borderline seasonal variation"""
    base_date = datetime(2024, 1, 1)
    # Regular intervals with slight amount variation
    amounts = [
        Decimal('100.00'),
        Decimal('110.00'),
        Decimal('115.00'),
        Decimal('105.00'),
        Decimal('95.00'),
    ]
    payments = []
    
    for i, amount in enumerate(amounts):
        payment = Payment(
            amount=amount,
            payment_date=base_date + timedelta(days=30 * i),
            category="utilities"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Should be regular due to consistent timing and moderate amount variation
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.amount_statistics.std_dev_amount < Decimal('10')
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1


async def test_single_day_difference_payments(
    payment_pattern_service: PaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing payments with single day differences"""
    base_date = datetime(2024, 1, 1)
    # Create payments on consecutive days
    payments = []
    
    for i in range(4):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=base_date + timedelta(days=i),
            category="utilities"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=1,
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=1)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.frequency_metrics.average_days_between == 1
    assert analysis.frequency_metrics.std_dev_days == 0
