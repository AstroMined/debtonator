from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select

from src.models.accounts import Account
from src.models.payments import Payment, PaymentSource
from src.models.transaction_history import TransactionHistory
from src.services.realtime_cashflow import RealtimeCashflowService

@pytest.mark.asyncio
async def test_analyze_account_correlations(db_session):
    """Test account correlation analysis."""
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        available_credit=Decimal("1500.00"),
        total_limit=Decimal("2000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add_all([checking, credit])
    await db_session.commit()

    # Create test transfers
    payment = Payment(
        amount=Decimal("100.00"),
        payment_date=datetime.now().date(),
        category="Transfer",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(payment)
    await db_session.commit()

    source = PaymentSource(
        payment_id=payment.id,
        account_id=checking.id,
        amount=Decimal("100.00"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(source)
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    correlations = await service.analyze_account_correlations()

    assert correlations
    assert str(checking.id) in correlations
    assert str(credit.id) in correlations[str(checking.id)]
    correlation = correlations[str(checking.id)][str(credit.id)]
    assert correlation.relationship_type in ["complementary", "supplementary", "independent"]

@pytest.mark.asyncio
async def test_analyze_transfer_patterns(db_session):
    """Test transfer pattern analysis."""
    # Create test accounts and transfers
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add(account)
    await db_session.commit()

    # Create multiple transfers
    for _ in range(3):
        payment = Payment(
            amount=Decimal("50.00"),
            payment_date=datetime.now().date(),
            category="Transfer",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(payment)
        await db_session.commit()

        source = PaymentSource(
            payment_id=payment.id,
            account_id=account.id,
            amount=Decimal("50.00"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(source)
        await db_session.commit()

    service = RealtimeCashflowService(db_session)
    patterns = await service.analyze_transfer_patterns()

    assert patterns
    assert len(patterns) > 0
    pattern = patterns[0]
    assert pattern.source_account_id == account.id
    assert pattern.average_amount == Decimal("50.00")
    assert pattern.frequency == 3

@pytest.mark.asyncio
async def test_analyze_usage_patterns(db_session):
    """Test account usage pattern analysis."""
    # Create test account
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add(account)
    await db_session.commit()

    # Create test transactions
    transactions = [
        TransactionHistory(
            account_id=account.id,
            amount=Decimal("100.00"),
            transaction_type="debit",
            description="Grocery Store",
            transaction_date=datetime.now() - timedelta(days=i),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(5)
    ]
    db_session.add_all(transactions)
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    patterns = await service.analyze_usage_patterns()

    assert patterns
    assert account.id in patterns
    pattern = patterns[account.id]
    assert pattern.account_id == account.id
    assert pattern.average_transaction_size == Decimal("100.00")
    assert "Grocery Store" in pattern.common_merchants

@pytest.mark.asyncio
async def test_analyze_balance_distribution(db_session):
    """Test balance distribution analysis."""
    # Create test account
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add(account)
    await db_session.commit()

    # Create test transactions with varying amounts
    amounts = [Decimal("100.00"), Decimal("200.00"), Decimal("150.00")]
    transactions = [
        TransactionHistory(
            account_id=account.id,
            amount=amount,
            transaction_type="debit",
            description="Test Transaction",
            transaction_date=datetime.now() - timedelta(days=i),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i, amount in enumerate(amounts)
    ]
    db_session.add_all(transactions)
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    distributions = await service.analyze_balance_distribution()

    assert distributions
    assert account.id in distributions
    distribution = distributions[account.id]
    assert distribution.account_id == account.id
    assert distribution.min_balance_30d == min(amounts)
    assert distribution.max_balance_30d == max(amounts)

@pytest.mark.asyncio
async def test_assess_account_risks(db_session):
    """Test account risk assessment."""
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("100.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-1500.00"),
        available_credit=Decimal("500.00"),
        total_limit=Decimal("2000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add_all([checking, credit])
    await db_session.commit()

    # Create test transactions
    transactions = [
        TransactionHistory(
            account_id=checking.id,
            amount=Decimal("50.00"),
            transaction_type="debit",
            description="Test Transaction",
            transaction_date=datetime.now() - timedelta(days=i),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        for i in range(3)
    ]
    db_session.add_all(transactions)
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    risks = await service.assess_account_risks()

    assert risks
    assert checking.id in risks
    assert credit.id in risks
    
    checking_risk = risks[checking.id]
    assert checking_risk.account_id == checking.id
    assert checking_risk.overdraft_risk >= Decimal(0)
    assert checking_risk.overdraft_risk <= Decimal(1)
    assert checking_risk.overall_risk_score >= Decimal(0)
    assert checking_risk.overall_risk_score <= Decimal(1)

    credit_risk = risks[credit.id]
    assert credit_risk.account_id == credit.id
    assert credit_risk.credit_utilization_risk is not None
    assert credit_risk.credit_utilization_risk >= Decimal(0)
    assert credit_risk.credit_utilization_risk <= Decimal(1)

@pytest.mark.asyncio
async def test_get_cross_account_analysis(db_session):
    """Test comprehensive cross-account analysis."""
    # Create test account
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now().date(),
        updated_at=datetime.now().date()
    )
    db_session.add(account)
    await db_session.commit()

    # Create test transactions
    transaction = TransactionHistory(
        account_id=account.id,
        amount=Decimal("100.00"),
        transaction_type="debit",
        description="Test Transaction",
        transaction_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(transaction)
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    analysis = await service.get_cross_account_analysis()

    assert analysis
    assert isinstance(analysis.correlations, dict)
    assert isinstance(analysis.transfer_patterns, list)
    assert isinstance(analysis.usage_patterns, dict)
    assert isinstance(analysis.balance_distribution, dict)
    assert isinstance(analysis.risk_assessment, dict)
    assert analysis.timestamp == datetime.now().date()
