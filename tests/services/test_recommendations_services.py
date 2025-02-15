from datetime import date, timedelta, datetime
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability, LiabilityStatus
from src.models.payments import Payment, PaymentSource
from src.models.categories import Category
from src.schemas.recommendations import ConfidenceLevel
from src.schemas.payment_patterns import PatternType
from src.services.recommendations import RecommendationService


@pytest.fixture(scope="function")
async def recommendation_service(db_session: AsyncSession):
    return RecommendationService(db_session)


@pytest.fixture(scope="function")
async def test_accounts(db_session: AsyncSession):
    accounts = [
        Account(
            name="Test Credit",
            type="credit",
            available_balance=Decimal("-500"),
            total_limit=Decimal("1000"),
            available_credit=Decimal("500"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
    ]
    for account in accounts:
        db_session.add(account)
    await db_session.commit()
    return accounts


@pytest.fixture(scope="function")
async def test_bill(db_session: AsyncSession, base_category: Category, test_accounts):
    bill = Liability(
        name="Test Bill",
        amount=Decimal("100"),
        due_date=date.today() + timedelta(days=15),
        description="Test bill for recommendations",
        category_id=base_category.id,
        active=True,  # This bill should be active
        status=LiabilityStatus.PENDING,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        primary_account_id=test_accounts[0].id,  # Use credit account as primary
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(bill)
    await db_session.commit()
    return bill


@pytest.fixture(scope="function")
async def test_payments(db_session: AsyncSession, test_bill, test_accounts):
    """Create a consistent payment pattern: always 5 days before due date."""
    payments = []
    days_before_due = 5  # Consistent pattern of paying 5 days before due
    
    # Create 6 monthly payments
    for i in range(6):
        # Calculate this month's due date
        due_date = date.today() + timedelta(days=15)  # Always 15 days from today
        # Calculate payment date to be exactly 5 days before due date
        payment_date = due_date - timedelta(days=days_before_due)
        
        # Set the bill's due date
        test_bill.due_date = due_date
        await db_session.commit()
        
        print(f"Creating payment {i+1}: payment_date={payment_date}, due_date={due_date}, days_before={days_before_due}")
        
        # Create payment with exact timing
        payment = Payment(
            liability_id=test_bill.id,
            amount=Decimal("100"),
            payment_date=payment_date,  # Exactly 5 days before due date
            category="utilities",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(payment)
        await db_session.commit()

        # Add payment source
        source = PaymentSource(
            payment_id=payment.id,
            account_id=test_accounts[0].id,  # Use credit account
            amount=Decimal("100"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(source)
        await db_session.commit()
        
        payments.append(payment)
    
    return payments


@pytest.mark.asyncio
async def test_get_bill_payment_recommendations(
    recommendation_service: RecommendationService,
    test_bill,
    test_accounts,
    test_payments,
):
    """Test generating bill payment recommendations."""
    # First get the pattern directly
    pattern = await recommendation_service.pattern_service.analyze_bill_payments(test_bill.id)
    print(f"\nPattern: {pattern}")

    # Verify pattern detection
    assert pattern is not None
    assert pattern.pattern_type == PatternType.REGULAR
    assert pattern.confidence_score >= 0.9  # High confidence due to consistent pattern
    assert abs(pattern.frequency_metrics.average_days_between - 5) < 0.1  # Close to 5 days
    assert pattern.frequency_metrics.std_dev_days < 0.1  # Very low deviation

    # Get recommendations
    response = await recommendation_service.get_bill_payment_recommendations()
    assert response is not None
    assert len(response.recommendations) > 0
    
    recommendation = response.recommendations[0]
    assert recommendation.bill_id == test_bill.id
    assert recommendation.confidence == ConfidenceLevel.HIGH
    assert recommendation.affected_accounts == [test_accounts[0].id]
    
    # Should recommend payment 5 days before due date based on pattern
    expected_date = test_bill.due_date - timedelta(days=5)
    assert recommendation.recommended_date == expected_date
    
    # Verify recommendation details
    assert "Highly consistent payment pattern" in recommendation.reason
    assert "5 days before due date" in recommendation.reason
    assert recommendation.historical_pattern_strength >= 0.9


@pytest.mark.asyncio
async def test_impact_metrics_calculation(
    recommendation_service: RecommendationService,
    test_bill,
    test_accounts,
    test_payments,
):
    """Test calculation of recommendation impact metrics."""
    response = await recommendation_service.get_bill_payment_recommendations()
    assert response is not None
    assert len(response.recommendations) > 0
    
    recommendation = response.recommendations[0]
    impact = recommendation.impact
    
    assert impact is not None
    assert isinstance(impact.balance_impact, Decimal)
    assert isinstance(impact.risk_score, Decimal)
    assert 0 <= impact.risk_score <= 100
    
    # Credit account should have utilization impact
    assert impact.credit_utilization_impact is not None


@pytest.mark.asyncio
async def test_confidence_scoring(
    recommendation_service: RecommendationService,
):
    """Test confidence level to decimal conversion."""
    high_score = recommendation_service._confidence_to_decimal(
        ConfidenceLevel.HIGH
    )
    medium_score = recommendation_service._confidence_to_decimal(
        ConfidenceLevel.MEDIUM
    )
    low_score = recommendation_service._confidence_to_decimal(
        ConfidenceLevel.LOW
    )
    
    assert high_score == Decimal("1.0")
    assert medium_score == Decimal("0.6")
    assert low_score == Decimal("0.3")


@pytest.mark.asyncio
async def test_credit_utilization_calculation(
    recommendation_service: RecommendationService,
    test_accounts,
):
    """Test credit utilization calculation."""
    credit_accounts = [
        acc for acc in test_accounts if acc.type == "credit"
    ]
    
    utilization = recommendation_service._calculate_credit_utilization(
        credit_accounts
    )
    
    # With -500 balance and 1000 limit, utilization should be 50%
    assert utilization == Decimal("50")
    
    # Test with balance adjustment
    adjusted_utilization = recommendation_service._calculate_credit_utilization(
        credit_accounts, Decimal("100")
    )
    
    # Additional 100 should increase utilization to 60%
    assert adjusted_utilization == Decimal("60")
