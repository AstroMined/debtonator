"""
Integration tests for the CashflowForecastRepository.

This module contains tests for the CashflowForecastRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
CashflowForecastRepository, ensuring proper validation flow and data integrity.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cashflow import CashflowForecast
from src.repositories.cashflow import CashflowForecastRepository
# Import schemas and schema factories - essential part of the validation pattern
from src.schemas.cashflow.base import CashflowCreate, CashflowUpdate
from tests.helpers.datetime_utils import datetime_equals, datetime_greater_than
from tests.helpers.schema_factories.cashflow.base import (
    create_cashflow_schema, create_cashflow_update_schema)

pytestmark = pytest.mark.asyncio


async def test_create_cashflow_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
):
    """Test creating a cashflow forecast with proper validation flow."""
    # 1. ARRANGE: Setup test data
    forecast_date = datetime.now(timezone.utc)

    # 2. SCHEMA: Create and validate through Pydantic schema
    forecast_schema = create_cashflow_schema(
        forecast_date=forecast_date,
        total_bills=Decimal("1100.00"),
        total_income=Decimal("1600.00"),
        balance=Decimal("2200.00"),
        forecast=Decimal("2700.00"),
        min_14_day=Decimal("550.00"),
        min_30_day=Decimal("1100.00"),
        min_60_day=Decimal("2200.00"),
        min_90_day=Decimal("3300.00"),
        daily_deficit=Decimal("28.00"),
        yearly_deficit=Decimal("10220.00"),
        required_income=Decimal("13500.00"),
        hourly_rate_40=Decimal("22.00"),
        hourly_rate_30=Decimal("29.33"),
        hourly_rate_20=Decimal("44.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = forecast_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await cashflow_forecast_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.forecast_date is not None
    assert result.total_bills == Decimal("1100.00")
    assert result.total_income == Decimal("1600.00")
    assert result.balance == Decimal("2200.00")
    assert result.forecast == Decimal("2700.00")
    assert result.min_14_day == Decimal("550.00")
    assert result.min_30_day == Decimal("1100.00")
    assert result.min_60_day == Decimal("2200.00")
    assert result.min_90_day == Decimal("3300.00")
    assert result.daily_deficit == Decimal("28.00")
    assert result.yearly_deficit == Decimal("10220.00")
    assert result.required_income == Decimal("13500.00")
    assert result.hourly_rate_40 == Decimal("22.00")
    assert result.hourly_rate_30 == Decimal("29.33")
    assert result.hourly_rate_20 == Decimal("44.00")
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_cashflow_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_cashflow_forecast: CashflowForecast,
):
    """Test retrieving a cashflow forecast by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the cashflow forecast
    result = await cashflow_forecast_repository.get(test_cashflow_forecast.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_cashflow_forecast.id
    assert result.forecast_date is not None
    assert result.total_bills == test_cashflow_forecast.total_bills
    assert result.total_income == test_cashflow_forecast.total_income
    assert result.balance == test_cashflow_forecast.balance
    assert result.forecast == test_cashflow_forecast.forecast


async def test_update_cashflow_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_cashflow_forecast: CashflowForecast,
):
    """Test updating a cashflow forecast with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_cashflow_forecast.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_cashflow_update_schema(
        total_bills=Decimal("1200.00"),
        total_income=Decimal("1700.00"),
        balance=Decimal("2300.00"),
        daily_deficit=Decimal("30.00"),
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await cashflow_forecast_repository.update(
        test_cashflow_forecast.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_cashflow_forecast.id
    assert result.total_bills == Decimal("1200.00")
    assert result.total_income == Decimal("1700.00")
    assert result.balance == Decimal("2300.00")
    assert result.daily_deficit == Decimal("30.00")
    # These fields should remain unchanged
    assert result.min_14_day == test_cashflow_forecast.min_14_day
    assert result.min_30_day == test_cashflow_forecast.min_30_day
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_cashflow_forecast(
    cashflow_forecast_repository: CashflowForecastRepository,
    test_cashflow_forecast: CashflowForecast,
):
    """Test deleting a cashflow forecast."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the cashflow forecast
    result = await cashflow_forecast_repository.delete(test_cashflow_forecast.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_forecast = await cashflow_forecast_repository.get(test_cashflow_forecast.id)
    assert deleted_forecast is None
