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



@pytest.mark.asyncio
async def test_cashflow_forecast_creation(test_cashflow_forecast: CashflowForecast):
    """Test basic cashflow forecast creation"""
    assert isinstance(test_cashflow_forecast, CashflowForecast)
    assert test_cashflow_forecast.total_bills == Decimal('1000.00')
    assert test_cashflow_forecast.total_income == Decimal('800.00')
    assert test_cashflow_forecast.balance == Decimal('-200.00')




@pytest.mark.asyncio
async def test_cashflow_forecast_fields(test_cashflow_forecast: CashflowForecast):
    """Test the model fields for CashflowForecast (data structure only)"""
    # Verify field data types and values
    assert isinstance(test_cashflow_forecast.forecast_date, datetime)
    assert isinstance(test_cashflow_forecast.total_bills, Decimal)
    assert isinstance(test_cashflow_forecast.total_income, Decimal)
    assert isinstance(test_cashflow_forecast.balance, Decimal)
    assert isinstance(test_cashflow_forecast.forecast, Decimal)
    assert isinstance(test_cashflow_forecast.min_14_day, Decimal)
    assert isinstance(test_cashflow_forecast.min_30_day, Decimal)
    assert isinstance(test_cashflow_forecast.min_60_day, Decimal)
    assert isinstance(test_cashflow_forecast.min_90_day, Decimal)
    assert isinstance(test_cashflow_forecast.daily_deficit, Decimal)
    assert isinstance(test_cashflow_forecast.yearly_deficit, Decimal)
    assert isinstance(test_cashflow_forecast.required_income, Decimal)
    assert isinstance(test_cashflow_forecast.hourly_rate_40, Decimal)
    assert isinstance(test_cashflow_forecast.hourly_rate_30, Decimal)
    assert isinstance(test_cashflow_forecast.hourly_rate_20, Decimal)
    
    # Verify initial values
    assert test_cashflow_forecast.total_bills == Decimal('1000.00')
    assert test_cashflow_forecast.total_income == Decimal('800.00')
    assert test_cashflow_forecast.balance == Decimal('-200.00')

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
