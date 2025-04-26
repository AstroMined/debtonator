from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
from src.models.payments import Payment, PaymentSource
from src.services.cashflow.cashflow_historical_service import HistoricalService


@pytest.fixture
async def setup_test_data(db_session: AsyncSession):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
    )
    savings = Account(
        name="Test Savings",
        type="savings",
        available_balance=Decimal("5000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
    )
    db_session.add_all([checking, savings])
    await db_session.flush()

    # Create test payments
    base_date = datetime.now(ZoneInfo("UTC")) - timedelta(days=90)
    payments = []
    payment_sources = []

    # Regular monthly payment pattern
    for i in range(3):
        payment = Payment(
            amount=Decimal("500.00"),
            payment_date=base_date + timedelta(days=30 * i),
            category="utilities",
            description="Monthly utility payment",
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        )
        payments.append(payment)

        source = PaymentSource(
            account_id=checking.id,
            amount=Decimal("500.00"),
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        )
        payment_sources.append((payment, source))

    # Holiday season increased spending
    holiday_date = datetime(base_date.year, 12, 20, tzinfo=ZoneInfo("UTC"))
    holiday_payment = Payment(
        amount=Decimal("1000.00"),
        payment_date=holiday_date,
        category="shopping",
        description="Holiday shopping",
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
    )
    payments.append(holiday_payment)

    holiday_source = PaymentSource(
        account_id=checking.id,
        amount=Decimal("1000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC")),
    )
    payment_sources.append((holiday_payment, holiday_source))

    # Add payments to session
    db_session.add_all(payments)
    await db_session.flush()

    # Add payment sources and link to payments
    for payment, source in payment_sources:
        source.payment_id = payment.id
        db_session.add(source)

    # Create test income entries
    income_entries = [
        Income(
            date=base_date + timedelta(days=2),  # Early income in first period
            source="Salary",
            amount=Decimal("3000.00"),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            account_id=checking.id,
            recurring=True,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        ),
        Income(
            date=base_date + timedelta(days=45),
            source="Salary",
            amount=Decimal("3000.00"),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            account_id=checking.id,
            recurring=True,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        ),
        Income(
            date=base_date + timedelta(days=75),
            source="Bonus",
            amount=Decimal("1000.00"),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            account_id=savings.id,
            recurring=False,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        ),
    ]
    db_session.add_all(income_entries)
    await db_session.commit()

    return {"checking": checking, "savings": savings, "base_date": base_date}


@pytest.mark.asyncio
async def test_historical_trends_analysis(db_session: AsyncSession, setup_test_data):
    service = HistoricalService(db_session)
    base_date = setup_test_data["base_date"]
    now = datetime.now(ZoneInfo("UTC"))

    # Get historical trends for both accounts
    # Print the date range we're analyzing
    print(f"\nAnalyzing date range: {base_date} to {now}")

    trends = await service.get_historical_trends(
        account_ids=[setup_test_data["checking"].id, setup_test_data["savings"].id],
        start_date=base_date,
        end_date=now,
    )

    # Verify trend metrics
    assert trends.metrics.trend_direction in ["increasing", "decreasing", "stable"]
    assert 0 <= trends.metrics.trend_strength <= 1
    assert trends.metrics.confidence_score > 0

    # Verify period analysis
    assert len(trends.period_analysis) > 0
    first_period = trends.period_analysis[0]
    assert first_period.period_start >= base_date
    assert first_period.total_inflow > 0
    assert first_period.total_outflow > 0

    # Verify seasonality
    assert len(trends.seasonality.monthly_patterns) == 12
    assert len(trends.seasonality.day_of_week_patterns) == 7
    assert len(trends.seasonality.day_of_month_patterns) == 31
    assert 0 <= trends.seasonality.seasonal_strength <= 1


@pytest.mark.asyncio
async def test_historical_trends_empty_data(db_session: AsyncSession):
    service = HistoricalService(db_session)
    now = datetime.now(ZoneInfo("UTC"))

    # Create an account with no transactions
    account = Account(
        name="Empty Account",
        type="checking",
        available_balance=Decimal("0.00"),
        created_at=now,
        updated_at=now,
    )
    db_session.add(account)
    await db_session.commit()

    # Verify that attempting to analyze an account with no data raises an error
    with pytest.raises(
        ValueError, match="No transactions available for trend analysis"
    ):
        await service.get_historical_trends(
            account_ids=[account.id], start_date=now - timedelta(days=30), end_date=now
        )


@pytest.mark.asyncio
async def test_historical_trends_significant_events(
    db_session: AsyncSession, setup_test_data
):
    service = HistoricalService(db_session)
    base_date = setup_test_data["base_date"]
    now = datetime.now(ZoneInfo("UTC"))

    trends = await service.get_historical_trends(
        account_ids=[setup_test_data["checking"].id], start_date=base_date, end_date=now
    )

    # Verify that the holiday payment was detected as a significant event
    holiday_events = [
        event
        for period in trends.period_analysis
        for event in period.significant_events
        if "shopping" in event["description"].lower()
    ]
    # Print all transactions for debugging
    transactions = await service._get_historical_transactions(
        account_ids=[setup_test_data["checking"].id], start_date=base_date, end_date=now
    )
    print("\nTransactions:")
    for t in transactions:
        print(f"{t['date']}: {t['amount']} ({t['type']} - {t['category']})")

    # Print significant events for debugging
    print("\nSignificant events:")
    for period in trends.period_analysis:
        for event in period.significant_events:
            print(f"{event['date']}: {event['description']}")

    assert len(holiday_events) > 0


@pytest.mark.asyncio
async def test_historical_trends_seasonal_patterns(
    db_session: AsyncSession, setup_test_data
):
    service = HistoricalService(db_session)
    base_date = setup_test_data["base_date"]
    now = datetime.now(ZoneInfo("UTC"))

    trends = await service.get_historical_trends(
        account_ids=[setup_test_data["checking"].id], start_date=base_date, end_date=now
    )

    # Verify monthly patterns
    december_impact = trends.seasonality.monthly_patterns[12]  # December
    assert (
        abs(december_impact) > 0
    ), "Expected significant impact in December due to holiday spending"

    # Verify holiday impacts
    # Print holiday impacts for debugging
    print("\nHoliday impacts:", trends.seasonality.holiday_impacts)

    assert "christmas" in trends.seasonality.holiday_impacts
    assert abs(trends.seasonality.holiday_impacts["christmas"]) > 0
