import pytest
from datetime import date
from decimal import Decimal

from src.models.cashflow import CashflowForecast

@pytest.fixture
def cashflow_forecast():
    """Create a test cashflow forecast instance"""
    return CashflowForecast(
        forecast_date=date.today(),
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

@pytest.mark.asyncio
async def test_cashflow_forecast_creation(cashflow_forecast):
    """Test basic cashflow forecast creation"""
    assert isinstance(cashflow_forecast, CashflowForecast)
    assert cashflow_forecast.total_bills == Decimal('1000.00')
    assert cashflow_forecast.total_income == Decimal('800.00')
    assert cashflow_forecast.balance == Decimal('-200.00')

@pytest.mark.asyncio
async def test_calculate_deficits_negative(cashflow_forecast):
    """Test deficit calculations with negative minimum amount"""
    cashflow_forecast.calculate_deficits()
    # Takes minimum of all min_X_day values (-600) and divides by 14
    expected_daily = Decimal('-600.00') / 14
    assert cashflow_forecast.daily_deficit == expected_daily
    assert cashflow_forecast.yearly_deficit == expected_daily * 365

@pytest.mark.asyncio
async def test_calculate_deficits_positive(cashflow_forecast):
    """Test deficit calculations with positive minimum amount"""
    # Set all minimum values to positive numbers
    cashflow_forecast.min_14_day = Decimal('300.00')
    cashflow_forecast.min_30_day = Decimal('400.00')
    cashflow_forecast.min_60_day = Decimal('500.00')
    cashflow_forecast.min_90_day = Decimal('600.00')
    
    cashflow_forecast.calculate_deficits()
    assert cashflow_forecast.daily_deficit == Decimal('0')
    assert cashflow_forecast.yearly_deficit == Decimal('0')

@pytest.mark.asyncio
async def test_calculate_required_income(cashflow_forecast):
    """Test required income calculation"""
    # Set up yearly deficit
    cashflow_forecast.yearly_deficit = Decimal('-52000.00')  # -$52,000/year
    cashflow_forecast.calculate_required_income()
    # Required income should be abs(-52000)/0.8 to account for taxes
    expected = abs(Decimal('-52000.00')) / Decimal('0.8')  # $65,000
    assert cashflow_forecast.required_income == expected

@pytest.mark.asyncio
async def test_calculate_hourly_rates(cashflow_forecast):
    """Test hourly rate calculations for different work hours"""
    # Set required income to $65,000
    cashflow_forecast.required_income = Decimal('65000.00')
    cashflow_forecast.calculate_hourly_rates()
    
    # Weekly required = 65000/52 = 1250
    weekly = Decimal('65000.00') / 52
    
    # Test each hourly rate
    assert cashflow_forecast.hourly_rate_40 == weekly / 40  # ~$31.25/hr
    assert cashflow_forecast.hourly_rate_30 == weekly / 30  # ~$41.67/hr
    assert cashflow_forecast.hourly_rate_20 == weekly / 20  # ~$62.50/hr
