from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cashflow import CashflowForecast


@pytest_asyncio.fixture
async def test_cashflow_forecast(
    db_session: AsyncSession,
) -> CashflowForecast:
    """Fixture to create a test cashflow forecast."""
    # Create a naive datetime for DB storage
    forecast_date = datetime.now(timezone.utc).replace(tzinfo=None)

    # Create model instance directly
    forecast = CashflowForecast(
        forecast_date=forecast_date,
        total_bills=Decimal("1000.00"),
        total_income=Decimal("1500.00"),
        balance=Decimal("2000.00"),
        forecast=Decimal("2500.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("25.00"),
        yearly_deficit=Decimal("9125.00"),
        required_income=Decimal("12000.00"),
        hourly_rate_40=Decimal("20.00"),
        hourly_rate_30=Decimal("26.67"),
        hourly_rate_20=Decimal("40.00"),
    )

    # Add to session manually
    db_session.add(forecast)
    await db_session.flush()
    await db_session.refresh(forecast)

    return forecast


@pytest_asyncio.fixture
async def test_multiple_forecasts(
    db_session: AsyncSession,
) -> List[CashflowForecast]:
    """Fixture to create multiple cashflow forecasts for testing."""
    now = datetime.now(timezone.utc)

    # Create multiple forecasts with various dates
    forecast_data = [
        {
            "forecast_date": now - timedelta(days=10),
            "total_bills": Decimal("900.00"),
            "total_income": Decimal("1300.00"),
            "balance": Decimal("1800.00"),
            "forecast": Decimal("2200.00"),
            "min_14_day": Decimal("450.00"),
            "min_30_day": Decimal("900.00"),
            "min_60_day": Decimal("1800.00"),
            "min_90_day": Decimal("2700.00"),
            "daily_deficit": Decimal("20.00"),
            "yearly_deficit": Decimal("7300.00"),
            "required_income": Decimal("10000.00"),
            "hourly_rate_40": Decimal("17.00"),
            "hourly_rate_30": Decimal("22.67"),
            "hourly_rate_20": Decimal("34.00"),
        },
        {
            "forecast_date": now - timedelta(days=7),
            "total_bills": Decimal("950.00"),
            "total_income": Decimal("1400.00"),
            "balance": Decimal("1900.00"),
            "forecast": Decimal("2350.00"),
            "min_14_day": Decimal("475.00"),
            "min_30_day": Decimal("950.00"),
            "min_60_day": Decimal("1900.00"),
            "min_90_day": Decimal("2850.00"),
            "daily_deficit": Decimal("22.00"),
            "yearly_deficit": Decimal("8030.00"),
            "required_income": Decimal("11000.00"),
            "hourly_rate_40": Decimal("18.50"),
            "hourly_rate_30": Decimal("24.67"),
            "hourly_rate_20": Decimal("37.00"),
        },
        {
            "forecast_date": now - timedelta(days=3),
            "total_bills": Decimal("1000.00"),
            "total_income": Decimal("1500.00"),
            "balance": Decimal("2000.00"),
            "forecast": Decimal("2500.00"),
            "min_14_day": Decimal("500.00"),
            "min_30_day": Decimal("1000.00"),
            "min_60_day": Decimal("2000.00"),
            "min_90_day": Decimal("3000.00"),
            "daily_deficit": Decimal("25.00"),
            "yearly_deficit": Decimal("9125.00"),
            "required_income": Decimal("12000.00"),
            "hourly_rate_40": Decimal("20.00"),
            "hourly_rate_30": Decimal("26.67"),
            "hourly_rate_20": Decimal("40.00"),
        },
        {
            "forecast_date": now,
            "total_bills": Decimal("1050.00"),
            "total_income": Decimal("1550.00"),
            "balance": Decimal("2100.00"),
            "forecast": Decimal("2600.00"),
            "min_14_day": Decimal("525.00"),
            "min_30_day": Decimal("1050.00"),
            "min_60_day": Decimal("2100.00"),
            "min_90_day": Decimal("3150.00"),
            "daily_deficit": Decimal("27.00"),
            "yearly_deficit": Decimal("9855.00"),
            "required_income": Decimal("13000.00"),
            "hourly_rate_40": Decimal("21.50"),
            "hourly_rate_30": Decimal("28.67"),
            "hourly_rate_20": Decimal("43.00"),
        },
    ]

    # Create the forecasts using direct model instantiation
    created_forecasts = []
    for data in forecast_data:
        # Make datetime naive for DB storage
        naive_date = data["forecast_date"].replace(tzinfo=None)

        # Create model instance directly
        forecast = CashflowForecast(
            forecast_date=naive_date,
            total_bills=data["total_bills"],
            total_income=data["total_income"],
            balance=data["balance"],
            forecast=data["forecast"],
            min_14_day=data["min_14_day"],
            min_30_day=data["min_30_day"],
            min_60_day=data["min_60_day"],
            min_90_day=data["min_90_day"],
            daily_deficit=data["daily_deficit"],
            yearly_deficit=data["yearly_deficit"],
            required_income=data["required_income"],
            hourly_rate_40=data["hourly_rate_40"],
            hourly_rate_30=data["hourly_rate_30"],
            hourly_rate_20=data["hourly_rate_20"],
        )

        # Add to session manually
        db_session.add(forecast)
        created_forecasts.append(forecast)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for forecast in created_forecasts:
        await db_session.refresh(forecast)

    return created_forecasts
