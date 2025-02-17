import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cashflow import CashflowForecast
from src.models.base_model import naive_utc_now, naive_utc_from_date

pytestmark = pytest.mark.asyncio

async def test_cashflow_repr(test_cashflow_forecast: CashflowForecast):
    """Test string representation of CashflowForecast"""
    expected_repr = f"<CashflowForecast {test_cashflow_forecast.forecast_date} balance={test_cashflow_forecast.balance}>"
    assert repr(test_cashflow_forecast) == expected_repr

async def test_forecast_date_index(db_session: AsyncSession):
    """Test that forecast_date index is working"""
    # Create multiple forecasts
    date1 = naive_utc_from_date(2025, 3, 15)
    date2 = naive_utc_from_date(2025, 3, 16)
    
    forecasts = [
        CashflowForecast(
            forecast_date=date,
            total_bills=Decimal('1000.00'),
            total_income=Decimal('800.00'),
            balance=Decimal('-200.00'),
            forecast=Decimal('-200.00'),
            min_14_day=Decimal('-300.00'),
            min_30_day=Decimal('-400.00'),
            min_60_day=Decimal('-500.00'),
            min_90_day=Decimal('-600.00'),
            daily_deficit=Decimal('0'),
            yearly_deficit=Decimal('0'),
            required_income=Decimal('0'),
            hourly_rate_40=Decimal('0'),
            hourly_rate_30=Decimal('0'),
            hourly_rate_20=Decimal('0')
        )
        for date in [date1, date2]
    ]
    
    db_session.add_all(forecasts)
    await db_session.commit()
    
    # Query using forecast_date
    query = select(CashflowForecast).where(CashflowForecast.forecast_date == date1)
    result = await db_session.execute(query)
    forecast = result.scalar_one()
    
    assert forecast.forecast_date == date1

async def test_full_calculation_chain(test_cashflow_forecast: CashflowForecast):
    """Test full chain of calculations from deficits to hourly rates"""
    # Calculate deficits
    test_cashflow_forecast.calculate_deficits()
    assert test_cashflow_forecast.daily_deficit < 0
    assert test_cashflow_forecast.yearly_deficit < 0
    
    # Calculate required income
    test_cashflow_forecast.calculate_required_income()
    assert test_cashflow_forecast.required_income > 0
    assert test_cashflow_forecast.required_income == abs(test_cashflow_forecast.yearly_deficit) / Decimal('0.8')
    
    # Calculate hourly rates
    test_cashflow_forecast.calculate_hourly_rates()
    weekly_required = test_cashflow_forecast.required_income / 52
    assert test_cashflow_forecast.hourly_rate_40 == weekly_required / 40
    assert test_cashflow_forecast.hourly_rate_30 == weekly_required / 30
    assert test_cashflow_forecast.hourly_rate_20 == weekly_required / 20


@pytest.mark.asyncio
async def test_cashflow_forecast_creation(test_cashflow_forecast: CashflowForecast):
    """Test basic cashflow forecast creation"""
    assert isinstance(test_cashflow_forecast, CashflowForecast)
    assert test_cashflow_forecast.total_bills == Decimal('1000.00')
    assert test_cashflow_forecast.total_income == Decimal('800.00')
    assert test_cashflow_forecast.balance == Decimal('-200.00')

@pytest.mark.asyncio
async def test_calculate_deficits_negative(test_cashflow_forecast: CashflowForecast):
    """Test deficit calculations with negative minimum amount"""
    test_cashflow_forecast.calculate_deficits()
    # Takes minimum of all min_X_day values (-600) and divides by 14
    expected_daily = Decimal('-600.00') / 14
    assert test_cashflow_forecast.daily_deficit == expected_daily
    assert test_cashflow_forecast.yearly_deficit == expected_daily * 365

@pytest.mark.asyncio
async def test_calculate_deficits_positive(test_cashflow_forecast: CashflowForecast):
    """Test deficit calculations with positive minimum amount"""
    # Set all minimum values to positive numbers
    test_cashflow_forecast.min_14_day = Decimal('300.00')
    test_cashflow_forecast.min_30_day = Decimal('400.00')
    test_cashflow_forecast.min_60_day = Decimal('500.00')
    test_cashflow_forecast.min_90_day = Decimal('600.00')
    
    test_cashflow_forecast.calculate_deficits()
    assert test_cashflow_forecast.daily_deficit == Decimal('0')
    assert test_cashflow_forecast.yearly_deficit == Decimal('0')

@pytest.mark.asyncio
async def test_calculate_required_income(test_cashflow_forecast: CashflowForecast):
    """Test required income calculation"""
    # Set up yearly deficit
    test_cashflow_forecast.yearly_deficit = Decimal('-52000.00')  # -$52,000/year
    test_cashflow_forecast.calculate_required_income()
    # Required income should be abs(-52000)/0.8 to account for taxes
    expected = abs(Decimal('-52000.00')) / Decimal('0.8')  # $65,000
    assert test_cashflow_forecast.required_income == expected

@pytest.mark.asyncio
async def test_calculate_hourly_rates(test_cashflow_forecast: CashflowForecast):
    """Test hourly rate calculations for different work hours"""
    # Set required income to $65,000
    test_cashflow_forecast.required_income = Decimal('65000.00')
    test_cashflow_forecast.calculate_hourly_rates()
    
    # Weekly required = 65000/52 = 1250
    weekly = Decimal('65000.00') / 52
    
    # Test each hourly rate
    assert test_cashflow_forecast.hourly_rate_40 == weekly / 40  # ~$31.25/hr
    assert test_cashflow_forecast.hourly_rate_30 == weekly / 30  # ~$41.67/hr
    assert test_cashflow_forecast.hourly_rate_20 == weekly / 20  # ~$62.50/hr

@pytest.mark.asyncio
async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in cashflow forecast"""
    # Create forecast with explicit datetime values
    forecast = CashflowForecast(
        forecast_date=naive_utc_from_date(2025, 3, 15),
        total_bills=Decimal('1000.00'),
        total_income=Decimal('800.00'),
        balance=Decimal('-200.00'),
        forecast=Decimal('-200.00'),
        min_14_day=Decimal('-300.00'),
        min_30_day=Decimal('-400.00'),
        min_60_day=Decimal('-500.00'),
        min_90_day=Decimal('-600.00'),
        daily_deficit=Decimal('0'),
        yearly_deficit=Decimal('0'),
        required_income=Decimal('0'),
        hourly_rate_40=Decimal('0'),
        hourly_rate_30=Decimal('0'),
        hourly_rate_20=Decimal('0')
    )

    db_session.add(forecast)
    await db_session.commit()
    await db_session.refresh(forecast)

    # Verify all datetime fields are naive (no tzinfo)
    assert forecast.forecast_date.tzinfo is None
    assert forecast.created_at.tzinfo is None
    assert forecast.updated_at.tzinfo is None

    # Verify forecast_date components
    assert forecast.forecast_date.year == 2025
    assert forecast.forecast_date.month == 3
    assert forecast.forecast_date.day == 15
    assert forecast.forecast_date.hour == 0
    assert forecast.forecast_date.minute == 0
    assert forecast.forecast_date.second == 0
