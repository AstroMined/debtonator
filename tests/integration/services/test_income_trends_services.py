from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.models.income import Income
from src.schemas.income_trends import IncomeTrendsRequest
from src.services.income_trends import IncomeTrendsService
from src.utils.datetime_utils import utc_datetime


@pytest.fixture(scope="function")
def weekly_income_data():
    """Generate weekly income test data"""
    base_date = date(2024, 1, 1)
    return [
        Income(
            date=base_date + timedelta(weeks=i),
            source="Weekly Job",
            amount=Decimal("1000.00"),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            created_at=base_date,
            updated_at=base_date,
            account_id=1,
        )
        for i in range(12)  # 12 weeks of data
    ]


@pytest.fixture(scope="function")
def monthly_income_data():
    """Generate monthly income test data"""
    base_date = date(2024, 1, 1)
    return [
        Income(
            date=base_date + timedelta(days=30 * i),
            source="Rental Income",
            amount=Decimal("2000.00"),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            created_at=base_date,
            updated_at=base_date,
            account_id=1,
        )
        for i in range(12)  # 12 months of data
    ]


@pytest.fixture(scope="function")
def irregular_income_data():
    """Generate irregular income test data"""
    base_date = date(2024, 1, 1)
    amounts = [
        "500.00",
        "750.00",
        "300.00",
        "1200.00",
        "450.00",
        "800.00",
        "600.00",
        "900.00",
    ]
    intervals = [5, 12, 8, 15, 7, 20, 10]  # Irregular intervals

    dates = [base_date]
    for interval in intervals:
        dates.append(dates[-1] + timedelta(days=interval))

    return [
        Income(
            date=dates[i],
            source="Freelance Work",
            amount=Decimal(amounts[i]),
            deposited=True,
            undeposited_amount=Decimal("0.00"),
            created_at=base_date,
            updated_at=base_date,
            account_id=1,
        )
        for i in range(len(dates))
    ]


async def test_analyze_weekly_pattern(db_session, weekly_income_data):
    """Test detection of weekly income patterns"""
    # Arrange
    service = IncomeTrendsService(db_session)
    for income in weekly_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert len(result.patterns) > 0
    weekly_pattern = next(p for p in result.patterns if p.source == "Weekly Job")
    assert weekly_pattern.frequency == "weekly"
    assert weekly_pattern.confidence_score > 0.8
    assert weekly_pattern.average_amount == Decimal("1000.00")


async def test_analyze_monthly_pattern(db_session, monthly_income_data):
    """Test detection of monthly income patterns"""
    # Arrange
    service = IncomeTrendsService(db_session)
    for income in monthly_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert len(result.patterns) > 0
    monthly_pattern = next(p for p in result.patterns if p.source == "Rental Income")
    assert monthly_pattern.frequency == "monthly"
    assert monthly_pattern.confidence_score > 0.8
    assert monthly_pattern.average_amount == Decimal("2000.00")


async def test_analyze_irregular_pattern(db_session, irregular_income_data):
    """Test detection of irregular income patterns"""
    # Arrange
    service = IncomeTrendsService(db_session)
    for income in irregular_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert len(result.patterns) > 0
    irregular_pattern = next(p for p in result.patterns if p.source == "Freelance Work")
    assert irregular_pattern.frequency == "irregular"
    assert irregular_pattern.confidence_score < 0.5


async def test_source_statistics(db_session, weekly_income_data, monthly_income_data):
    """Test calculation of source statistics"""
    # Arrange
    service = IncomeTrendsService(db_session)
    for income in weekly_income_data + monthly_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert len(result.source_statistics) == 2
    weekly_stats = next(s for s in result.source_statistics if s.source == "Weekly Job")
    monthly_stats = next(
        s for s in result.source_statistics if s.source == "Rental Income"
    )

    assert weekly_stats.total_occurrences == 12
    assert weekly_stats.average_amount == Decimal("1000.00")
    assert weekly_stats.reliability_score > 0.8

    assert monthly_stats.total_occurrences == 12
    assert monthly_stats.average_amount == Decimal("2000.00")
    assert monthly_stats.reliability_score > 0.8


async def test_seasonality_analysis(db_session, monthly_income_data):
    """Test seasonality analysis with varying monthly amounts"""
    # Arrange
    service = IncomeTrendsService(db_session)

    # Modify some months to create seasonal pattern (using 1-based month numbers)
    monthly_income_data[5].amount = Decimal("2500.00")  # June (month 6) peak
    monthly_income_data[6].amount = Decimal("2500.00")  # July (month 7) peak
    monthly_income_data[7].amount = Decimal("2500.00")  # August (month 8) peak
    monthly_income_data[0].amount = Decimal("1500.00")  # January (month 1) trough
    monthly_income_data[1].amount = Decimal("1500.00")  # February (month 2) trough

    # Set the correct month in the date field
    for i, income in enumerate(monthly_income_data):
        income.date = date(2024, i + 1, 1)  # Set to first day of each month

    for income in monthly_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert result.seasonality is not None
    assert 6 in result.seasonality.peak_months  # June
    assert 7 in result.seasonality.peak_months  # July
    assert 8 in result.seasonality.peak_months  # August
    assert 1 in result.seasonality.trough_months  # January
    assert 2 in result.seasonality.trough_months  # February
    assert result.seasonality.confidence_score > 0.6


async def test_empty_data_handling(db_session):
    """Test handling of empty data set"""
    # Arrange
    service = IncomeTrendsService(db_session)
    request = IncomeTrendsRequest(
        start_date=utc_datetime(2024, 1, 1), end_date=utc_datetime(2024, 12, 31)
    )

    # Act & Assert
    with pytest.raises(ValueError, match="No income records found"):
        await service.analyze_trends(request)


async def test_filtered_source_analysis(
    db_session, weekly_income_data, monthly_income_data
):
    """Test analysis filtered by source"""
    # Arrange
    service = IncomeTrendsService(db_session)
    for income in weekly_income_data + monthly_income_data:
        db_session.add(income)
    await db_session.commit()

    request = IncomeTrendsRequest(
        start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), source="Weekly Job"
    )

    # Act
    result = await service.analyze_trends(request)

    # Assert
    assert len(result.patterns) == 1
    assert result.patterns[0].source == "Weekly Job"
    assert len(result.source_statistics) == 1
    assert result.source_statistics[0].source == "Weekly Job"
