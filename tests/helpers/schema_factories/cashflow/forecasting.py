"""
Forecasting schema factory functions.

This module provides factory functions for creating valid forecasting-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from src.schemas.cashflow.forecasting import (AccountForecastMetrics,
                                              AccountForecastRequest,
                                              AccountForecastResponse,
                                              AccountForecastResult,
                                              CustomForecastParameters,
                                              CustomForecastResponse,
                                              CustomForecastResult)
from tests.helpers.schema_factories.base import (MEDIUM_AMOUNT, SMALL_AMOUNT,
                                                 factory_function, utc_now)


@factory_function(CustomForecastParameters)
def create_custom_forecast_parameters_schema(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_pending: bool = True,
    account_ids: Optional[List[int]] = None,
    categories: Optional[List[str]] = None,
    confidence_threshold: Optional[Decimal] = None,
    include_recurring: bool = True,
    include_historical_patterns: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CustomForecastParameters schema instance.

    Args:
        start_date: Start date for the forecast (defaults to current UTC date)
        end_date: End date for the forecast (defaults to 90 days from start)
        include_pending: Whether to include pending transactions
        account_ids: Specific accounts to include in forecast
        categories: Specific categories to include in forecast
        confidence_threshold: Minimum confidence level (0-1 scale)
        include_recurring: Whether to include recurring transactions
        include_historical_patterns: Whether to use historical patterns
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CustomForecastParameters schema
    """
    now = utc_now()
    if start_date is None:
        start_date = now
    if end_date is None:
        end_date = start_date + timedelta(days=90)

    if confidence_threshold is None:
        confidence_threshold = Decimal("0.8")

    data = {
        "start_date": start_date,
        "end_date": end_date,
        "include_pending": include_pending,
        "confidence_threshold": confidence_threshold,
        "include_recurring": include_recurring,
        "include_historical_patterns": include_historical_patterns,
        **kwargs,
    }

    if account_ids is not None:
        data["account_ids"] = account_ids

    if categories is not None:
        data["categories"] = categories

    return data


@factory_function(CustomForecastResult)
def create_custom_forecast_result_schema(
    date: Optional[datetime] = None,
    projected_balance: Optional[Decimal] = None,
    projected_income: Optional[Decimal] = None,
    projected_expenses: Optional[Decimal] = None,
    confidence_score: Optional[Decimal] = None,
    contributing_factors: Optional[Dict[str, Decimal]] = None,
    risk_factors: Optional[Dict[str, Decimal]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CustomForecastResult schema instance for a single date.

    Args:
        date: Date of this forecast point (defaults to current UTC date)
        projected_balance: Projected balance on this date (defaults to 1500.00)
        projected_income: Projected income for this date (defaults to 200.00)
        projected_expenses: Projected expenses for this date (defaults to 150.00)
        confidence_score: Confidence score for this point (defaults to 0.85)
        contributing_factors: Factors contributing to forecast and weights
        risk_factors: Risk factors for this forecast and weights
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CustomForecastResult schema
    """
    if date is None:
        date = utc_now()

    if projected_balance is None:
        projected_balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00

    if projected_income is None:
        projected_income = MEDIUM_AMOUNT * Decimal("2")  # 200.00

    if projected_expenses is None:
        projected_expenses = MEDIUM_AMOUNT * Decimal("1.5")  # 150.00

    if confidence_score is None:
        confidence_score = Decimal("0.85")

    if contributing_factors is None:
        contributing_factors = {
            "Historical Patterns": Decimal("0.4"),
            "Recurring Transactions": Decimal("0.35"),
            "Pending Transactions": Decimal("0.15"),
            "Seasonal Factors": Decimal("0.1"),
        }

    if risk_factors is None:
        risk_factors = {
            "Timing Uncertainty": Decimal("0.3"),
            "Amount Variance": Decimal("0.25"),
            "Unexpected Expenses": Decimal("0.35"),
            "Income Delay": Decimal("0.1"),
        }

    data = {
        "date": date,
        "projected_balance": projected_balance,
        "projected_income": projected_income,
        "projected_expenses": projected_expenses,
        "confidence_score": confidence_score,
        "contributing_factors": contributing_factors,
        "risk_factors": risk_factors,
        **kwargs,
    }

    return data


@factory_function(CustomForecastResponse)
def create_custom_forecast_response_schema(
    parameters: Optional[Dict[str, Any]] = None,
    results: Optional[List[Dict[str, Any]]] = None,
    overall_confidence: Optional[Decimal] = None,
    summary_statistics: Optional[Dict[str, Decimal]] = None,
    timestamp: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CustomForecastResponse schema instance.

    Args:
        parameters: Parameters used for this forecast
        results: Daily forecast results
        overall_confidence: Overall confidence score (defaults to 0.82)
        summary_statistics: Summary statistics for the forecast period
        timestamp: When this forecast was generated (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CustomForecastResponse schema
    """
    if parameters is None:
        parameters = create_custom_forecast_parameters_schema().model_dump()

    if results is None:
        # Create a series of daily forecasts
        now = utc_now()
        results = []
        for i in range(5):  # Just create 5 for testing
            day_result = create_custom_forecast_result_schema(
                date=now + timedelta(days=i),
                # Gradually increasing balance
                projected_balance=MEDIUM_AMOUNT * Decimal(15 + i),
            ).model_dump()
            results.append(day_result)

    if overall_confidence is None:
        overall_confidence = Decimal("0.82")

    if summary_statistics is None:
        summary_statistics = {
            "average_daily_balance": MEDIUM_AMOUNT * Decimal("17"),  # 1700.00
            "minimum_balance": MEDIUM_AMOUNT * Decimal("15"),  # 1500.00
            "maximum_balance": MEDIUM_AMOUNT * Decimal("19"),  # 1900.00
            "total_income": MEDIUM_AMOUNT * Decimal("10"),  # 1000.00
            "total_expenses": MEDIUM_AMOUNT * Decimal("6"),  # 600.00
            "net_change": MEDIUM_AMOUNT * Decimal("4"),  # 400.00
        }

    if timestamp is None:
        timestamp = utc_now()

    data = {
        "parameters": parameters,
        "results": results,
        "overall_confidence": overall_confidence,
        "summary_statistics": summary_statistics,
        "timestamp": timestamp,
        **kwargs,
    }

    return data


@factory_function(AccountForecastRequest)
def create_account_forecast_request_schema(
    account_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_pending: bool = True,
    include_recurring: bool = True,
    include_transfers: bool = True,
    confidence_threshold: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountForecastRequest schema instance.

    Args:
        account_id: ID of the account to forecast
        start_date: Start date for the forecast (defaults to current UTC date)
        end_date: End date for the forecast (defaults to 90 days from start)
        include_pending: Whether to include pending transactions
        include_recurring: Whether to include recurring transactions
        include_transfers: Whether to include inter-account transfers
        confidence_threshold: Minimum confidence level (defaults to 0.8)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountForecastRequest schema
    """
    now = utc_now()
    if start_date is None:
        start_date = now
    if end_date is None:
        end_date = start_date + timedelta(days=90)
    if confidence_threshold is None:
        confidence_threshold = Decimal("0.8")

    data = {
        "account_id": account_id,
        "start_date": start_date,
        "end_date": end_date,
        "include_pending": include_pending,
        "include_recurring": include_recurring,
        "include_transfers": include_transfers,
        "confidence_threshold": confidence_threshold,
        **kwargs,
    }

    return data


@factory_function(AccountForecastMetrics)
def create_account_forecast_metrics_schema(
    average_daily_balance: Optional[Decimal] = None,
    minimum_projected_balance: Optional[Decimal] = None,
    maximum_projected_balance: Optional[Decimal] = None,
    average_inflow: Optional[Decimal] = None,
    average_outflow: Optional[Decimal] = None,
    projected_low_balance_dates: Optional[List[datetime]] = None,
    credit_utilization: Optional[Decimal] = None,
    balance_volatility: Optional[Decimal] = None,
    forecast_confidence: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountForecastMetrics schema instance.

    Args:
        average_daily_balance: Average daily balance (defaults to 1500.00)
        minimum_projected_balance: Minimum balance (defaults to 1000.00)
        maximum_projected_balance: Maximum balance (defaults to 2000.00)
        average_inflow: Average daily money coming in (defaults to 100.00)
        average_outflow: Average daily money going out (defaults to 80.00)
        projected_low_balance_dates: Dates with projected low balances
        credit_utilization: Projected credit utilization
        balance_volatility: Projected volatility (defaults to 300.00)
        forecast_confidence: Overall confidence (defaults to 0.85)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountForecastMetrics schema
    """
    if average_daily_balance is None:
        average_daily_balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00

    if minimum_projected_balance is None:
        minimum_projected_balance = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if maximum_projected_balance is None:
        maximum_projected_balance = MEDIUM_AMOUNT * Decimal("20")  # 2000.00

    if average_inflow is None:
        average_inflow = MEDIUM_AMOUNT  # 100.00

    if average_outflow is None:
        average_outflow = MEDIUM_AMOUNT * Decimal("0.8")  # 80.00

    if projected_low_balance_dates is None:
        now = utc_now()
        projected_low_balance_dates = [
            now + timedelta(days=10),
            now + timedelta(days=25),
            now + timedelta(days=40),
        ]

    if balance_volatility is None:
        balance_volatility = MEDIUM_AMOUNT * Decimal("3")  # 300.00

    if forecast_confidence is None:
        forecast_confidence = Decimal("0.85")

    data = {
        "average_daily_balance": average_daily_balance,
        "minimum_projected_balance": minimum_projected_balance,
        "maximum_projected_balance": maximum_projected_balance,
        "average_inflow": average_inflow,
        "average_outflow": average_outflow,
        "projected_low_balance_dates": projected_low_balance_dates,
        "balance_volatility": balance_volatility,
        "forecast_confidence": forecast_confidence,
        **kwargs,
    }

    if credit_utilization is not None:
        data["credit_utilization"] = credit_utilization

    return data


@factory_function(AccountForecastResult)
def create_account_forecast_result_schema(
    date: Optional[datetime] = None,
    projected_balance: Optional[Decimal] = None,
    projected_inflow: Optional[Decimal] = None,
    projected_outflow: Optional[Decimal] = None,
    confidence_score: Optional[Decimal] = None,
    contributing_transactions: Optional[List[Dict[str, Union[Decimal, str]]]] = None,
    warning_flags: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountForecastResult schema instance for a single date.

    Args:
        date: Date of this forecast point (defaults to current UTC date)
        projected_balance: Projected balance (defaults to 1500.00)
        projected_inflow: Projected incoming money (defaults to 100.00)
        projected_outflow: Projected outgoing money (defaults to 80.00)
        confidence_score: Confidence score (defaults to 0.85)
        contributing_transactions: Transactions contributing to forecast
        warning_flags: Warning indicators for this forecast point
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountForecastResult schema
    """
    if date is None:
        date = utc_now()

    if projected_balance is None:
        projected_balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00

    if projected_inflow is None:
        projected_inflow = MEDIUM_AMOUNT  # 100.00

    if projected_outflow is None:
        projected_outflow = MEDIUM_AMOUNT * Decimal("0.8")  # 80.00

    if confidence_score is None:
        confidence_score = Decimal("0.85")

    if contributing_transactions is None:
        contributing_transactions = [
            {
                "description": "Salary Deposit",
                "amount": MEDIUM_AMOUNT * Decimal("10"),  # 1000.00
                "type": "income",
            },
            {
                "description": "Rent Payment",
                "amount": MEDIUM_AMOUNT * Decimal("8"),  # 800.00
                "type": "expense",
            },
            {
                "description": "Utility Bill",
                "amount": MEDIUM_AMOUNT * Decimal("1.5"),  # 150.00
                "type": "expense",
            },
        ]

    if warning_flags is None:
        warning_flags = []

    data = {
        "date": date,
        "projected_balance": projected_balance,
        "projected_inflow": projected_inflow,
        "projected_outflow": projected_outflow,
        "confidence_score": confidence_score,
        "contributing_transactions": contributing_transactions,
        "warning_flags": warning_flags,
        **kwargs,
    }

    return data


@factory_function(AccountForecastResponse)
def create_account_forecast_response_schema(
    account_id: int,
    forecast_period: Optional[Tuple[datetime, datetime]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    daily_forecasts: Optional[List[Dict[str, Any]]] = None,
    overall_confidence: Optional[Decimal] = None,
    timestamp: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountForecastResponse schema instance.

    Args:
        account_id: ID of the account
        forecast_period: Start and end dates of the forecast
        metrics: Summary metrics for the forecast
        daily_forecasts: Daily forecast results
        overall_confidence: Overall confidence score (defaults to 0.82)
        timestamp: When this forecast was generated (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountForecastResponse schema
    """
    now = utc_now()
    if forecast_period is None:
        start_date = now
        end_date = start_date + timedelta(days=90)
        forecast_period = (start_date, end_date)

    if metrics is None:
        metrics = create_account_forecast_metrics_schema().model_dump()

    if daily_forecasts is None:
        # Create a series of daily forecasts
        daily_forecasts = []
        for i in range(5):  # Just create 5 for testing
            day_result = create_account_forecast_result_schema(
                date=now + timedelta(days=i),
                # Gradually increasing balance
                projected_balance=MEDIUM_AMOUNT * Decimal(15 + i),
            ).model_dump()
            daily_forecasts.append(day_result)

    if overall_confidence is None:
        overall_confidence = Decimal("0.82")

    if timestamp is None:
        timestamp = utc_now()

    data = {
        "account_id": account_id,
        "forecast_period": forecast_period,
        "metrics": metrics,
        "daily_forecasts": daily_forecasts,
        "overall_confidence": overall_confidence,
        "timestamp": timestamp,
        **kwargs,
    }

    return data
