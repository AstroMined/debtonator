from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payments import Payment, PaymentSource
from src.models.liabilities import Liability, LiabilityStatus
from src.models.categories import Category
from src.models.accounts import Account
from src.schemas.payment_patterns import PaymentPatternRequest, PatternType
from src.services.payment_patterns import BillPaymentPatternService


@pytest.fixture(scope="function")
async def test_accounts(db_session: AsyncSession):
    """Create test accounts for payment patterns"""
    now = datetime.now(timezone.utc)
    accounts = [
        Account(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-500"),
            total_limit=Decimal("1000"),
            available_credit=Decimal("500"),
            created_at=now,
            updated_at=now
        ),
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000"),
            created_at=now,
            updated_at=now
        ),
    ]
    for account in accounts:
        db_session.add(account)
    await db_session.commit()
    return accounts


@pytest.fixture(scope="function")
async def test_bill(db_session: AsyncSession, base_category: Category, test_accounts):
    """Create a test bill for payment pattern analysis"""
    now = datetime.now(timezone.utc)
    bill = Liability(
        name="Test Bill",
        amount=Decimal("100"),
        due_date=(now + timedelta(days=15)).date(),
        description="Test bill for payment patterns",
        category_id=base_category.id,
        active=True,
        status=LiabilityStatus.PENDING,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        primary_account_id=test_accounts[0].id,  # Use credit account as primary
        created_at=now,
        updated_at=now
    )
    db_session.add(bill)
    await db_session.commit()
    return bill


@pytest.fixture(scope="function")
def payment_pattern_service(db_session: AsyncSession):
    return BillPaymentPatternService(db_session)


@pytest.fixture(scope="function")
async def regular_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create a set of regular monthly payments for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    payments = []
    
    for i in range(6):
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Pay 5 days before due date
        
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def irregular_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create a set of irregular payments with varying amounts and dates for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    amounts = [Decimal('75.50'), Decimal('120.25'), Decimal('95.75'), Decimal('150.00')]
    # Due dates are monthly, but payments are made at irregular intervals before due
    due_dates = [base_date + timedelta(days=30 * i) for i in range(4)]
    days_before = [3, 7, 2, 5]  # Irregular days before due date
    payments = []
    
    for amount, due_date, days in zip(amounts, due_dates, days_before):
        payment_date = due_date - timedelta(days=days)
        payment = Payment(
            amount=amount,
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def seasonal_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create a set of monthly payments with seasonal variations for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
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
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Consistent 5 days before due
        payment = Payment(
            amount=amount,
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        # Add payment source
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


async def test_analyze_regular_pattern(
    payment_pattern_service: BillPaymentPatternService,
    regular_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.confidence_score >= 0.8
    assert analysis.sample_size == 6  # Regular payments fixture creates 6 payments
    assert "consistent" in analysis.notes[0].lower()
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1
    assert analysis.amount_statistics.average_amount == Decimal('100.00')
    assert analysis.suggested_category == "utilities"


async def test_analyze_irregular_pattern(
    payment_pattern_service: BillPaymentPatternService,
    irregular_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
            category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.IRREGULAR
    assert analysis.confidence_score < 0.8
    assert analysis.sample_size == 4
    assert "irregular" in analysis.notes[0].lower()
    assert analysis.amount_statistics.min_amount == Decimal('75.50')
    assert analysis.amount_statistics.max_amount == Decimal('150.00')
    assert analysis.suggested_category == "utilities"  # Category used in fixture


async def test_analyze_seasonal_pattern(
    payment_pattern_service: BillPaymentPatternService,
    seasonal_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.SEASONAL
    assert analysis.confidence_score > 0.5
    assert analysis.sample_size == 6  # Fixture creates 6 monthly payments with increasing amounts
    assert any("seasonal" in note.lower() or "monthly" in note.lower() for note in analysis.notes)
    assert analysis.amount_statistics.min_amount == Decimal('100.00')
    assert analysis.amount_statistics.max_amount == Decimal('250.00')
    assert analysis.suggested_category == "utilities"


async def test_insufficient_data_pattern(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    # Create just one payment (below min_sample_size)
    due_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    payment_date = due_date - timedelta(days=5)
    payment = Payment(
        amount=Decimal('100.00'),
        payment_date=payment_date,
        category="misc",
        liability_id=test_bill.id,
        description=f"Due date: {due_date.date()}"
    )
    db_session.add(payment)
    # Add payment source
    source = PaymentSource(
        payment=payment,
        account_id=test_accounts[0].id,  # Use credit account
        amount=Decimal('100.00')
    )
    db_session.add(source)
    await db_session.commit()
    
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="misc",
        min_sample_size=3  # Require at least 3 samples
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.UNKNOWN
    assert analysis.confidence_score == 0.0
    assert analysis.sample_size == 1
    assert "insufficient data" in analysis.notes[0].lower()


async def test_date_range_filter(
    payment_pattern_service: BillPaymentPatternService,
    regular_payments,
    test_accounts
):
    # Get total number of payments first
    total_payments = len(regular_payments)
    
    # Create request with date range that should exclude some payments
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        start_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 4, 1, tzinfo=timezone.utc)
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Verify filtering worked
    assert analysis.sample_size < total_payments
    assert analysis.analysis_period_start >= datetime(2024, 2, 1, tzinfo=timezone.utc)
    assert analysis.analysis_period_end <= datetime(2024, 4, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="function")
async def mixed_interval_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create payments with mostly regular intervals but some outliers for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    # Due dates are monthly, payments made at varying intervals before due
    due_dates = [base_date + timedelta(days=30 * i) for i in range(6)]
    days_before = [5, 3, 7, 2, 6, 4]  # Varying days before due date
    payments = []
    
    for due_date, days in zip(due_dates, days_before):
        payment_date = due_date - timedelta(days=days)
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def minimal_regular_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create exactly 3 payments with regular intervals for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    payments = []
    
    for i in range(3):
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Consistently 5 days before due
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    return payments


@pytest.fixture(scope="function")
async def gapped_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create payments with a significant gap in the middle for a specific bill"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    # Monthly due dates
    due_dates = [base_date + timedelta(days=30 * i) for i in range(8)]
    # Skip payments for months 3, 4, and 5
    skip_months = {3, 4, 5}
    payments = []
    
    for i, due_date in enumerate(due_dates):
        if i not in skip_months:
            payment_date = due_date - timedelta(days=5)  # 5 days before due
            payment = Payment(
                amount=Decimal('100.00'),
                payment_date=payment_date,
                category="utilities",
                liability_id=test_bill.id,
                description=f"Due date: {due_date.date()}"
            )
            db_session.add(payment)
            source = PaymentSource(
                payment=payment,
                account_id=test_accounts[0].id,  # Use credit account
                amount=Decimal('100.00')
            )
            db_session.add(source)
            payments.append(payment)
    
    await db_session.commit()
    return payments


async def test_mixed_interval_pattern(
    payment_pattern_service: BillPaymentPatternService,
    mixed_interval_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert 0.6 <= analysis.confidence_score <= 0.8  # Lower confidence due to variations
    assert abs(analysis.frequency_metrics.average_days_between - 30) <= 3
    assert analysis.frequency_metrics.std_dev_days > 0


async def test_minimal_sample_regular_pattern(
    payment_pattern_service: BillPaymentPatternService,
    minimal_regular_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.confidence_score <= 0.5  # Lower confidence due to minimal sample size
    assert analysis.sample_size == 3
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1


async def test_gapped_payment_pattern(
    payment_pattern_service: BillPaymentPatternService,
    gapped_payments,
    test_accounts
):
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities"
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.IRREGULAR
    assert analysis.confidence_score < 0.6  # Lower confidence due to gap
    assert analysis.sample_size == 5  # Fixture creates 5 payments (skipping months 3, 4, and 5)
    assert any("irregular" in note.lower() for note in analysis.notes)  # Check for "irregular" in notes


async def test_analyze_bill_payments_no_payments(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession
):
    """Test analyzing a bill with no payments"""
    result = await payment_pattern_service.analyze_bill_payments(999)  # Non-existent liability_id
    assert result is None


async def test_analyze_bill_payments_with_pattern(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test analyzing a bill with regular payments"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    payments = []
    
    for i in range(3):  # Reduce to 3 payments to match test expectations
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Consistently 5 days before due
        payment = Payment(
            amount=Decimal('200.00'),
            payment_date=payment_date,
            category="rent",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('200.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    # Debug print
    query = select(Payment).where(Payment.liability_id == test_bill.id)
    debug_result = await db_session.execute(query)
    debug_payments = debug_result.scalars().all()
    print(f"\nDebug: Found {len(debug_payments)} payments in test: {[f'Payment({p.amount} on {p.payment_date})' for p in debug_payments]}")
    
    result = await payment_pattern_service.analyze_bill_payments(test_bill.id)
    
    assert result is not None
    assert result.pattern_type == PatternType.REGULAR
    assert result.sample_size == 3  # Explicitly check for 3 payments
    assert result.suggested_category == "rent"
    assert abs(result.frequency_metrics.average_days_between - 30) < 1


async def test_category_suggestion_mixed(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test category suggestion with mixed categories"""
    # Create payments with different categories
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    categories = ["utilities", "utilities", "utilities", "rent", "groceries"]
    payments = []
    
    for i, category in enumerate(categories):
        due_date = base_date + timedelta(days=30)  # Same due date for all
        payment_date = due_date - timedelta(days=5 + i)  # Different days before due
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category=category,
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.suggested_category == "utilities"  # Most frequent category


async def test_category_suggestion_no_categories(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test category suggestion with no categories"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    payments = []
    
    for i in range(3):
        due_date = base_date + timedelta(days=30)  # Same due date for all
        payment_date = due_date - timedelta(days=5 + i)  # Different days before due
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="uncategorized",  # Default category instead of None
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.suggested_category == "uncategorized"


async def test_analyze_same_day_payments(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test analyzing payments made on the same day"""
    # Create multiple payments on the same day
    due_date = datetime(2024, 1, 15, tzinfo=timezone.utc)
    payment_date = due_date - timedelta(days=5)  # All payments 5 days before due
    payments = []
    
    for i in range(3):
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.pattern_type == PatternType.UNKNOWN
    assert analysis.frequency_metrics.average_days_between == 0
    assert analysis.frequency_metrics.std_dev_days == 0


async def test_filter_combination(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test analyzing payments with multiple filter combinations"""
    # Create payments with various attributes
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    due_date = base_date + timedelta(days=30)  # Common due date
    payments = []
    
    for i in range(6):
        payment_date = base_date + timedelta(days=i)  # Different payment dates
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id if i < 3 else None,  # Mix of liability and non-liability payments
            description=f"Due date: {due_date.date()}" if i < 3 else None
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id if i % 2 == 0 else test_accounts[1].id,  # Mix of credit and checking accounts
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    # Test with multiple filters
    request = PaymentPatternRequest(
        account_id=test_accounts[0].id,
        category_id="utilities",
        liability_id=test_bill.id,
        start_date=base_date,
        end_date=base_date + timedelta(days=2)
    )
    
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.sample_size < 6  # Should be filtered
    assert analysis.analysis_period_start >= base_date
    assert analysis.analysis_period_end <= base_date + timedelta(days=2)


async def test_amount_statistics_edge_cases(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test amount statistics with edge case values"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    amounts = [
        Decimal('0.00'),  # Zero amount
        Decimal('999999.99'),  # Very large amount
        Decimal('0.01'),  # Very small amount
        Decimal('100.00'),  # Normal amount
    ]
    payments = []
    
    for i, amount in enumerate(amounts):
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Consistent 5 days before due
        payment = Payment(
            amount=amount,
            payment_date=payment_date,
            category="misc",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    assert analysis.amount_statistics.min_amount == Decimal('0.00')
    assert analysis.amount_statistics.max_amount == Decimal('999999.99')
    assert analysis.amount_statistics.std_dev_amount > Decimal('0')
    assert analysis.pattern_type == PatternType.SEASONAL  # High amount variation with regular timing


async def test_borderline_regular_pattern(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test pattern detection with borderline regular intervals"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    # Due dates are monthly, payments made at slightly varying intervals
    due_dates = [base_date + timedelta(days=30 * i) for i in range(5)]
    days_before = [4, 6, 3, 5, 7]  # Varying days before due date
    payments = []
    
    for due_date, days in zip(due_dates, days_before):
        payment_date = due_date - timedelta(days=days)
        payment = Payment(
            amount=Decimal('100.00'),
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal('100.00')
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Should still be detected as regular but with lower confidence
    assert analysis.pattern_type == PatternType.REGULAR
    assert 0.6 <= analysis.confidence_score <= 0.875  # Allow higher confidence for borderline cases
    assert abs(analysis.frequency_metrics.average_days_between - 30) <= 2


async def test_borderline_seasonal_pattern(
    payment_pattern_service: BillPaymentPatternService,
    db_session: AsyncSession,
    test_bill,
    test_accounts
):
    """Test pattern detection with borderline seasonal variation"""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
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
        due_date = base_date + timedelta(days=30 * i)
        payment_date = due_date - timedelta(days=5)  # Consistent 5 days before due
        payment = Payment(
            amount=amount,
            payment_date=payment_date,
            category="utilities",
            liability_id=test_bill.id,
            description=f"Due date: {due_date.date()}"
        )
        db_session.add(payment)
        source = PaymentSource(
            payment=payment,
            account_id=test_accounts[0].id,  # Use credit account
            amount=amount
        )
        db_session.add(source)
        payments.append(payment)
    
    await db_session.commit()
    
    request = PaymentPatternRequest(account_id=test_accounts[0].id)
    analysis = await payment_pattern_service.analyze_payment_patterns(request)
    
    # Should be regular due to consistent timing and moderate amount variation
    assert analysis.pattern_type == PatternType.REGULAR
    assert analysis.amount_statistics.std_dev_amount < Decimal('10')
    assert abs(analysis.frequency_metrics.average_days_between - 30) < 1
