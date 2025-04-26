from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cashflow import CashflowForecast
from src.services.cashflow.cashflow_metrics_service import MetricsService
from src.utils.datetime_utils import naive_utc_now


@pytest.fixture(scope="function")
async def test_cashflow_forecast():
    """Create a test cashflow forecast instance."""
    return CashflowForecast(
        forecast_date=naive_utc_now(),
        total_bills=Decimal("1000.00"),
        total_income=Decimal("800.00"),
        balance=Decimal("-200.00"),
        forecast=Decimal("-200.00"),
        min_14_day=Decimal("-300.00"),
        min_30_day=Decimal("-400.00"),
        min_60_day=Decimal("-500.00"),
        min_90_day=Decimal("-600.00"),
        daily_deficit=Decimal("0"),
        yearly_deficit=Decimal("0"),
        required_income=Decimal("0"),
        hourly_rate_40=Decimal("0"),
        hourly_rate_30=Decimal("0"),
        hourly_rate_20=Decimal("0"),
    )


@pytest.mark.asyncio
async def test_update_cashflow_deficits(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_deficits method with negative minimum amounts."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Use service method
    metrics_service.update_cashflow_deficits(test_cashflow_forecast)

    # Takes minimum of all min_X_day values (-600) and divides by 14
    # The service implementation should properly calculate the daily deficit
    expected_min = min(
        test_cashflow_forecast.min_14_day,
        test_cashflow_forecast.min_30_day,
        test_cashflow_forecast.min_60_day,
        test_cashflow_forecast.min_90_day,
    )
    expected_daily = metrics_service.calculate_daily_deficit(expected_min, 14)
    expected_yearly = metrics_service.calculate_yearly_deficit(expected_daily)

    assert test_cashflow_forecast.daily_deficit == expected_daily
    assert test_cashflow_forecast.yearly_deficit == expected_yearly
    # Sanity check: daily deficit should be positive (absolute value of negative min)
    assert test_cashflow_forecast.daily_deficit > 0
    # Sanity check: yearly deficit should be positive (daily * 365)
    assert test_cashflow_forecast.yearly_deficit > 0


@pytest.mark.asyncio
async def test_update_cashflow_deficits_positive(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_deficits method with positive minimum amounts."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Set all minimum values to positive numbers
    test_cashflow_forecast.min_14_day = Decimal("300.00")
    test_cashflow_forecast.min_30_day = Decimal("400.00")
    test_cashflow_forecast.min_60_day = Decimal("500.00")
    test_cashflow_forecast.min_90_day = Decimal("600.00")

    # Use service method
    metrics_service.update_cashflow_deficits(test_cashflow_forecast)

    # When min values are positive, daily and yearly deficits should be 0
    assert test_cashflow_forecast.daily_deficit == Decimal("0.00")
    assert test_cashflow_forecast.yearly_deficit == Decimal("0")


@pytest.mark.asyncio
async def test_update_cashflow_required_income(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_required_income method."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Set up yearly deficit
    test_cashflow_forecast.yearly_deficit = Decimal("52000.00")  # $52,000/year

    # Use service method
    metrics_service.update_cashflow_required_income(test_cashflow_forecast)

    # Required income should be 52000/0.8 to account for taxes
    expected = Decimal("52000.00") / Decimal("0.8")  # $65,000
    assert test_cashflow_forecast.required_income == expected


@pytest.mark.asyncio
async def test_update_cashflow_required_income_custom_tax(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_required_income method with custom tax rate."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Set up yearly deficit
    test_cashflow_forecast.yearly_deficit = Decimal("52000.00")  # $52,000/year

    # Use service method with custom tax rate
    metrics_service.update_cashflow_required_income(
        test_cashflow_forecast, Decimal("0.75")
    )

    # Required income should be 52000/0.75 to account for taxes
    expected = Decimal("52000.00") / Decimal("0.75")  # ~$69,333.33
    assert test_cashflow_forecast.required_income == expected


@pytest.mark.asyncio
async def test_update_cashflow_hourly_rates(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_hourly_rates method."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Set required income to $65,000
    test_cashflow_forecast.required_income = Decimal("65000.00")

    # Use service method
    metrics_service.update_cashflow_hourly_rates(test_cashflow_forecast)

    # Weekly required = 65000/52 = 1250
    weekly = Decimal("65000.00") / 52

    # Test each hourly rate
    assert test_cashflow_forecast.hourly_rate_40 == weekly / 40  # ~$31.25/hr
    assert test_cashflow_forecast.hourly_rate_30 == weekly / 30  # ~$41.67/hr
    assert test_cashflow_forecast.hourly_rate_20 == weekly / 20  # ~$62.50/hr


@pytest.mark.asyncio
async def test_update_cashflow_all_calculations(
    test_cashflow_forecast: CashflowForecast, db_session: AsyncSession
):
    """Test the update_cashflow_all_calculations method."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Use service method for full calculation chain
    metrics_service.update_cashflow_all_calculations(test_cashflow_forecast)

    # Verify the chain works end-to-end
    assert test_cashflow_forecast.daily_deficit > 0
    assert test_cashflow_forecast.yearly_deficit > 0
    assert test_cashflow_forecast.required_income > 0

    # Check the mathematical relationships
    assert (
        test_cashflow_forecast.yearly_deficit
        == test_cashflow_forecast.daily_deficit * 365
    )
    assert (
        test_cashflow_forecast.required_income
        == test_cashflow_forecast.yearly_deficit / Decimal("0.8")
    )

    # Check hourly rates
    weekly_required = test_cashflow_forecast.required_income / 52
    assert test_cashflow_forecast.hourly_rate_40 == weekly_required / 40
    assert test_cashflow_forecast.hourly_rate_30 == weekly_required / 30
    assert test_cashflow_forecast.hourly_rate_20 == weekly_required / 20


@pytest.mark.asyncio
async def test_calculate_daily_deficit_method(db_session: AsyncSession):
    """Test the calculate_daily_deficit method directly."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Test positive amount (should return 0)
    assert metrics_service.calculate_daily_deficit(Decimal("100.00"), 30) == Decimal(
        "0.00"
    )

    # Test negative amount
    assert metrics_service.calculate_daily_deficit(Decimal("-300.00"), 30) == Decimal(
        "10.00"
    )

    # Test zero amount
    assert metrics_service.calculate_daily_deficit(Decimal("0.00"), 30) == Decimal(
        "0.00"
    )


@pytest.mark.asyncio
async def test_calculate_yearly_deficit_method(db_session: AsyncSession):
    """Test the calculate_yearly_deficit method directly."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Test with daily deficit
    assert metrics_service.calculate_yearly_deficit(Decimal("10.00")) == Decimal(
        "3650.00"
    )

    # Test with zero
    assert metrics_service.calculate_yearly_deficit(Decimal("0.00")) == Decimal("0.00")


@pytest.mark.asyncio
async def test_calculate_required_income_method(db_session: AsyncSession):
    """Test the calculate_required_income method directly."""
    # Create metrics service
    metrics_service = MetricsService(db_session)

    # Test with default tax rate (0.80)
    assert metrics_service.calculate_required_income(Decimal("1000.00")) == Decimal(
        "1250.00"
    )

    # Test with custom tax rate
    result = metrics_service.calculate_required_income(
        Decimal("1000.00"), Decimal("0.70")
    )
    assert result == Decimal("1428.57142857142857142857143")  # 1000/0.7

    # Test with zero deficit
    assert metrics_service.calculate_required_income(Decimal("0.00")) == Decimal("0.00")
