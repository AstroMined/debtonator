"""
Integration tests for the CashflowForecastRepository.

This module contains tests for the CashflowForecastRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
CashflowForecastRepository, ensuring proper validation flow and data integrity.
"""

from decimal import Decimal
from typing import List

import pytest

from src.models.cashflow import CashflowForecast
from src.repositories.cashflow import CashflowForecastRepository

# Import schemas and schema factories - essential part of the validation pattern
from src.utils.datetime_utils import (
    datetime_equals,
    datetime_greater_than,
    days_ago,
    days_from_now,
    ensure_utc,
    start_of_day,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_date(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting a forecast for a specific date."""
    # 1. ARRANGE: Get a date from one of the test forecasts
    test_date = test_multiple_forecasts[2].forecast_date

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get forecast by date
    result = await cashflow_forecast_repository.get_by_date(test_date)

    # 4. ASSERT: Verify the operation results
    assert result is not None

    # Compare dates using the utility function, ignoring time components
    assert datetime_equals(
        start_of_day(result.forecast_date),
        start_of_day(test_date),
        ignore_timezone=True,
    )

    # Verify the correct forecast was retrieved
    assert result.total_bills == test_multiple_forecasts[2].total_bills
    assert result.total_income == test_multiple_forecasts[2].total_income


async def test_get_by_date_range(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting forecasts within a date range."""
    # 1. ARRANGE: Setup date range
    start_date = days_ago(8)
    end_date = days_from_now(1)

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get forecasts within date range
    results = await cashflow_forecast_repository.get_by_date_range(start_date, end_date)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 forecasts in this range

    # Verify dates are within the range
    for forecast in results:
        # Use datetime utility for consistent timezone handling
        assert datetime_greater_than(
            forecast.forecast_date, start_date, ignore_timezone=True
        ) or datetime_equals(forecast.forecast_date, start_date, ignore_timezone=True)

        assert datetime_greater_than(
            end_date, forecast.forecast_date, ignore_timezone=True
        ) or datetime_equals(end_date, forecast.forecast_date, ignore_timezone=True)


async def test_get_latest_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting the most recent forecast."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # Find the expected latest forecast from test data using datetime utility for consistent comparison
    test_forecasts_sorted = sorted(
        test_multiple_forecasts,
        key=lambda f: ensure_utc(f.forecast_date),
        reverse=True,
    )
    expected_latest = test_forecasts_sorted[0]

    # 3. ACT: Get the latest forecast
    result = await cashflow_forecast_repository.get_latest_forecast()

    # 4. ASSERT: Verify the operation results
    assert result is not None

    # Compare to the expected latest forecast
    assert result.id == expected_latest.id
    assert result.total_bills == expected_latest.total_bills
    assert result.total_income == expected_latest.total_income


async def test_get_forecast_trend(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting daily forecast trend over a period."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get forecast trend
    results = await cashflow_forecast_repository.get_forecast_trend(days=30)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 forecasts

    # Verify structure of results
    for result in results:
        assert "date" in result
        assert "forecast" in result
        assert "balance" in result
        assert "total_bills" in result
        assert "total_income" in result

    # Test with min values included
    results_with_min = await cashflow_forecast_repository.get_forecast_trend(
        days=30, include_min_values=True
    )

    # Verify min values are included
    for result in results_with_min:
        assert "min_14_day" in result
        assert "min_30_day" in result
        assert "min_60_day" in result
        assert "min_90_day" in result


async def test_get_deficit_trend(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting daily deficit trend over a period."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get deficit trend
    results = await cashflow_forecast_repository.get_deficit_trend(days=30)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 forecasts

    # Verify structure of results
    for result in results:
        assert "date" in result
        assert "daily_deficit" in result
        assert "yearly_deficit" in result
        assert "required_income" in result


async def test_get_required_income_trend(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting trend of required income over a period."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get required income trend
    results = await cashflow_forecast_repository.get_required_income_trend(days=30)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 forecasts

    # Verify structure of results
    for result in results:
        assert "date" in result
        assert "required_income" in result
        assert "hourly_rate_40" in result
        assert "hourly_rate_30" in result
        assert "hourly_rate_20" in result


async def test_get_min_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting minimum forecast values across all lookout periods."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get minimum forecast values
    results = await cashflow_forecast_repository.get_min_forecast(days=30)

    # 4. ASSERT: Verify the operation results
    assert "min_14_day" in results
    assert "min_30_day" in results
    assert "min_60_day" in results
    assert "min_90_day" in results

    # Calculate expected minimum values
    expected_min_14_day = min(f.min_14_day for f in test_multiple_forecasts)
    expected_min_30_day = min(f.min_30_day for f in test_multiple_forecasts)

    # Verify minimum values are correct
    assert results["min_14_day"] == expected_min_14_day
    assert results["min_30_day"] == expected_min_30_day


async def test_get_forecast_with_metrics(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_cashflow_forecast: CashflowForecast,
):
    """Test getting a forecast with additional calculated metrics."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get forecast with metrics
    result = await cashflow_forecast_repository.get_forecast_with_metrics()

    # 4. ASSERT: Verify the operation results
    assert "forecast" in result
    assert "date" in result
    assert "metrics" in result

    # Verify metrics structure
    metrics = result["metrics"]
    assert "income_to_bills_ratio" in metrics
    assert "deficit_percentage" in metrics
    assert "balance_to_min_ratio" in metrics
    assert "daily_deficit_to_income_ratio" in metrics

    # Test with specific date
    specific_date_result = await cashflow_forecast_repository.get_forecast_with_metrics(
        forecast_date=test_cashflow_forecast.forecast_date
    )

    # Verify specific forecast was retrieved
    assert specific_date_result["forecast"].id == test_cashflow_forecast.id


async def test_get_forecast_summary(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting a summary of forecasts over a period."""
    # 1. ARRANGE: Setup date range
    start_date = days_ago(15)
    end_date = days_from_now(1)

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get forecast summary
    result = await cashflow_forecast_repository.get_forecast_summary(
        start_date, end_date
    )

    # 4. ASSERT: Verify the operation results
    assert "period" in result
    assert "totals" in result
    assert "averages" in result
    assert "extremes" in result
    assert "minimums" in result

    # Verify period data
    period = result["period"]
    assert "start_date" in period
    assert "end_date" in period
    assert "days" in period

    # Verify totals data
    totals = result["totals"]
    assert "total_bills" in totals
    assert "total_income" in totals
    assert "deficit" in totals

    # Verify averages data
    averages = result["averages"]
    assert "avg_daily_deficit" in averages
    assert "avg_required_income" in averages

    # Verify extremes data
    extremes = result["extremes"]
    assert "min_balance" in extremes
    assert "min_forecast" in extremes
    assert "max_daily_deficit" in extremes

    # Verify minimums data
    minimums = result["minimums"]
    assert "min_14_day" in minimums
    assert "min_30_day" in minimums
    assert "min_60_day" in minimums
    assert "min_90_day" in minimums


async def test_get_forecast_by_account(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_multiple_forecasts: List[CashflowForecast],
):
    """Test getting account-specific forecast data."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures
    account_id = 1  # Test account ID

    # 3. ACT: Get account-specific forecast
    results = await cashflow_forecast_repository.get_forecast_by_account(
        account_id, days=30
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 forecasts

    # Verify account ID is set in results
    for result in results:
        assert "account_id" in result
        assert result["account_id"] == account_id
        assert "note" in result  # Current implementation includes a note


async def test_validation_error_handling():
    """Test handling invalid data that would normally be caught by schema validation."""
    # Try creating a schema with invalid data and expect it to fail validation
    try:
        # Use schema factory with invalid amount
        from tests.helpers.schema_factories.cashflow.base_schema_factories import (
            create_cashflow_schema,
        )

        invalid_schema = create_cashflow_schema(
            total_bills=Decimal("-100.00"),  # Invalid negative amount
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "total_bills" in str(e).lower() and "greater" in str(e).lower()
