"""
Base cashflow schema factory functions.

This module provides factory functions for creating valid Cashflow base
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.cashflow.cashflow_base import CashflowCreate, CashflowFilters, CashflowUpdate
from src.utils.datetime_utils import utc_now

from tests.helpers.schema_factories.base import (
    LARGE_AMOUNT,
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
    factory_function
)


@factory_function(CashflowCreate)
def create_cashflow_schema(
    total_bills: Optional[Decimal] = None,
    total_income: Optional[Decimal] = None,
    balance: Optional[Decimal] = None,
    forecast: Optional[Decimal] = None,
    min_14_day: Optional[Decimal] = None,
    min_30_day: Optional[Decimal] = None,
    min_60_day: Optional[Decimal] = None,
    min_90_day: Optional[Decimal] = None,
    daily_deficit: Optional[Decimal] = None,
    yearly_deficit: Optional[Decimal] = None,
    required_income: Optional[Decimal] = None,
    hourly_rate_40: Optional[Decimal] = None,
    hourly_rate_30: Optional[Decimal] = None,
    hourly_rate_20: Optional[Decimal] = None,
    forecast_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CashflowCreate schema instance.

    Args:
        total_bills: Total amount of bills in forecast period (defaults to 1000.00)
        total_income: Total amount of income in forecast period (defaults to 2000.00)
        balance: Current balance across all accounts (defaults to 1500.00)
        forecast: Projected balance at end of forecast period (defaults to 2500.00)
        min_14_day: Minimum funds required for next 14 days (defaults to 500.00)
        min_30_day: Minimum funds required for next 30 days (defaults to 1000.00)
        min_60_day: Minimum funds required for next 60 days (defaults to 2000.00)
        min_90_day: Minimum funds required for next 90 days (defaults to 3000.00)
        daily_deficit: Average daily deficit amount (defaults to 25.00)
        yearly_deficit: Projected yearly deficit (defaults to 9125.00)
        required_income: Income required with tax consideration (defaults to 12000.00)
        hourly_rate_40: Hourly rate at 40hrs/week (defaults to 20.00)
        hourly_rate_30: Hourly rate at 30hrs/week (defaults to 26.67)
        hourly_rate_20: Hourly rate at 20hrs/week (defaults to 40.00)
        forecast_date: Date of the forecast (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CashflowCreate schema
    """
    if total_bills is None:
        total_bills = MEDIUM_AMOUNT  # 100.00
    if total_income is None:
        total_income = LARGE_AMOUNT  # 1000.00
    if balance is None:
        balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    if forecast is None:
        forecast = MEDIUM_AMOUNT * Decimal("25")  # 2500.00
    if min_14_day is None:
        min_14_day = MEDIUM_AMOUNT * Decimal("5")  # 500.00
    if min_30_day is None:
        min_30_day = MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    if min_60_day is None:
        min_60_day = MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    if min_90_day is None:
        min_90_day = MEDIUM_AMOUNT * Decimal("30")  # 3000.00
    if daily_deficit is None:
        daily_deficit = SMALL_AMOUNT * Decimal("2.5")  # 25.00
    if yearly_deficit is None:
        yearly_deficit = daily_deficit * Decimal("365")  # ~9125.00
    if required_income is None:
        required_income = MEDIUM_AMOUNT * Decimal("120")  # 12000.00
    if hourly_rate_40 is None:
        hourly_rate_40 = SMALL_AMOUNT * Decimal("2")  # 20.00
    if hourly_rate_30 is None:
        hourly_rate_30 = Decimal("26.67")
    if hourly_rate_20 is None:
        hourly_rate_20 = SMALL_AMOUNT * Decimal("4")  # 40.00
    if forecast_date is None:
        forecast_date = utc_now()

    data = {
        "forecast_date": forecast_date,
        "total_bills": total_bills,
        "total_income": total_income,
        "balance": balance,
        "forecast": forecast,
        "min_14_day": min_14_day,
        "min_30_day": min_30_day,
        "min_60_day": min_60_day,
        "min_90_day": min_90_day,
        "daily_deficit": daily_deficit,
        "yearly_deficit": yearly_deficit,
        "required_income": required_income,
        "hourly_rate_40": hourly_rate_40,
        "hourly_rate_30": hourly_rate_30,
        "hourly_rate_20": hourly_rate_20,
        **kwargs,
    }

    return data


@factory_function(CashflowUpdate)
def create_cashflow_update_schema(
    total_bills: Optional[Decimal] = None,
    total_income: Optional[Decimal] = None,
    balance: Optional[Decimal] = None,
    forecast: Optional[Decimal] = None,
    min_14_day: Optional[Decimal] = None,
    min_30_day: Optional[Decimal] = None,
    min_60_day: Optional[Decimal] = None,
    min_90_day: Optional[Decimal] = None,
    daily_deficit: Optional[Decimal] = None,
    yearly_deficit: Optional[Decimal] = None,
    required_income: Optional[Decimal] = None,
    hourly_rate_40: Optional[Decimal] = None,
    hourly_rate_30: Optional[Decimal] = None,
    hourly_rate_20: Optional[Decimal] = None,
    forecast_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CashflowUpdate schema instance.

    All parameters are optional to allow partial updates.

    Args:
        total_bills: Updated total amount of bills
        total_income: Updated total amount of income
        balance: Updated current balance
        forecast: Updated projected balance
        min_14_day: Updated 14-day minimum funds
        min_30_day: Updated 30-day minimum funds
        min_60_day: Updated 60-day minimum funds
        min_90_day: Updated 90-day minimum funds
        daily_deficit: Updated daily deficit
        yearly_deficit: Updated yearly deficit
        required_income: Updated required income
        hourly_rate_40: Updated hourly rate at 40hrs/week
        hourly_rate_30: Updated hourly rate at 30hrs/week
        hourly_rate_20: Updated hourly rate at 20hrs/week
        forecast_date: Updated forecast date
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CashflowUpdate schema
    """
    data = {**kwargs}

    if total_bills is not None:
        data["total_bills"] = total_bills
    if total_income is not None:
        data["total_income"] = total_income
    if balance is not None:
        data["balance"] = balance
    if forecast is not None:
        data["forecast"] = forecast
    if min_14_day is not None:
        data["min_14_day"] = min_14_day
    if min_30_day is not None:
        data["min_30_day"] = min_30_day
    if min_60_day is not None:
        data["min_60_day"] = min_60_day
    if min_90_day is not None:
        data["min_90_day"] = min_90_day
    if daily_deficit is not None:
        data["daily_deficit"] = daily_deficit
    if yearly_deficit is not None:
        data["yearly_deficit"] = yearly_deficit
    if required_income is not None:
        data["required_income"] = required_income
    if hourly_rate_40 is not None:
        data["hourly_rate_40"] = hourly_rate_40
    if hourly_rate_30 is not None:
        data["hourly_rate_30"] = hourly_rate_30
    if hourly_rate_20 is not None:
        data["hourly_rate_20"] = hourly_rate_20
    if forecast_date is not None:
        data["forecast_date"] = forecast_date

    return data


@factory_function(CashflowFilters)
def create_cashflow_filters_schema(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_balance: Optional[Decimal] = None,
    max_balance: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CashflowFilters schema instance.

    Args:
        start_date: Filter cashflows starting from this date
        end_date: Filter cashflows until this date
        min_balance: Minimum balance threshold for filtering
        max_balance: Maximum balance threshold for filtering
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CashflowFilters schema
    """
    data = {**kwargs}

    if start_date is not None:
        data["start_date"] = start_date
    if end_date is not None:
        data["end_date"] = end_date
    if min_balance is not None:
        data["min_balance"] = min_balance
    if max_balance is not None:
        data["max_balance"] = max_balance

    return data
