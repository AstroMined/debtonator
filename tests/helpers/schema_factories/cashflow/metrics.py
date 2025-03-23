"""
Cashflow metrics schema factory functions.

This module provides factory functions for creating valid Cashflow metrics
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.cashflow.metrics import (DeficitCalculation, HourlyRates,
                                          MinimumRequired)
from tests.helpers.schema_factories.base import (MEDIUM_AMOUNT, SMALL_AMOUNT,
                                                 factory_function)


@factory_function(MinimumRequired)
def create_minimum_required_schema(
    min_14_day: Optional[Decimal] = None,
    min_30_day: Optional[Decimal] = None,
    min_60_day: Optional[Decimal] = None,
    min_90_day: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid MinimumRequired schema instance.

    Args:
        min_14_day: Minimum funds required for next 14 days (defaults to 500.00)
        min_30_day: Minimum funds required for next 30 days (defaults to 1000.00)
        min_60_day: Minimum funds required for next 60 days (defaults to 2000.00)
        min_90_day: Minimum funds required for next 90 days (defaults to 3000.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create MinimumRequired schema
    """
    if min_14_day is None:
        min_14_day = MEDIUM_AMOUNT * Decimal("5")  # 500.00
    if min_30_day is None:
        min_30_day = MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    if min_60_day is None:
        min_60_day = MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    if min_90_day is None:
        min_90_day = MEDIUM_AMOUNT * Decimal("30")  # 3000.00

    data = {
        "min_14_day": min_14_day,
        "min_30_day": min_30_day,
        "min_60_day": min_60_day,
        "min_90_day": min_90_day,
        **kwargs,
    }

    return data


@factory_function(DeficitCalculation)
def create_deficit_calculation_schema(
    daily_deficit: Optional[Decimal] = None,
    yearly_deficit: Optional[Decimal] = None,
    required_income: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid DeficitCalculation schema instance.

    Args:
        daily_deficit: Average daily deficit amount (defaults to 25.00)
        yearly_deficit: Projected yearly deficit (defaults to 9125.00)
        required_income: Income required with tax consideration (defaults to 12000.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create DeficitCalculation schema
    """
    if daily_deficit is None:
        daily_deficit = SMALL_AMOUNT * Decimal("2.5")  # 25.00
    if yearly_deficit is None:
        yearly_deficit = daily_deficit * Decimal("365")  # ~9125.00
    if required_income is None:
        required_income = MEDIUM_AMOUNT * Decimal("120")  # 12000.00

    data = {
        "daily_deficit": daily_deficit,
        "yearly_deficit": yearly_deficit,
        "required_income": required_income,
        **kwargs,
    }

    return data


@factory_function(HourlyRates)
def create_hourly_rates_schema(
    hourly_rate_40: Optional[Decimal] = None,
    hourly_rate_30: Optional[Decimal] = None,
    hourly_rate_20: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid HourlyRates schema instance.

    Args:
        hourly_rate_40: Hourly rate at 40hrs/week (defaults to 20.00)
        hourly_rate_30: Hourly rate at 30hrs/week (defaults to 26.67)
        hourly_rate_20: Hourly rate at 20hrs/week (defaults to 40.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create HourlyRates schema
    """
    if hourly_rate_40 is None:
        hourly_rate_40 = SMALL_AMOUNT * Decimal("2")  # 20.00
    if hourly_rate_30 is None:
        hourly_rate_30 = Decimal("26.67")
    if hourly_rate_20 is None:
        hourly_rate_20 = SMALL_AMOUNT * Decimal("4")  # 40.00

    data = {
        "hourly_rate_40": hourly_rate_40,
        "hourly_rate_30": hourly_rate_30,
        "hourly_rate_20": hourly_rate_20,
        **kwargs,
    }

    return data
