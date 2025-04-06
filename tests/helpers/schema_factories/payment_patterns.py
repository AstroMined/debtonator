"""
Payment pattern schema factory functions.

This module provides factory functions for creating valid PaymentPattern-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.payment_patterns import (
    AmountStatistics,
    FrequencyMetrics,
    PatternType,
    PaymentPatternAnalysis,
    PaymentPatternRequest,
    SeasonalMetrics,
)
from tests.helpers.schema_factories.base import factory_function
from src.utils.datetime_utils import utc_now


@factory_function(AmountStatistics)
def create_amount_statistics_schema(
    average_amount: Optional[Decimal] = None,
    std_dev_amount: Optional[Decimal] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    total_amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AmountStatistics schema instance.

    Args:
        average_amount: Average payment amount (defaults to 150.00)
        std_dev_amount: Standard deviation of payment amounts (defaults to 15.00)
        min_amount: Minimum payment amount (defaults to 100.00)
        max_amount: Maximum payment amount (defaults to 200.00)
        total_amount: Total amount of all payments (defaults to 1500.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AmountStatistics schema
    """
    if average_amount is None:
        average_amount = Decimal("150.00")
    if std_dev_amount is None:
        std_dev_amount = Decimal("15.00")
    if min_amount is None:
        min_amount = Decimal("100.00")
    if max_amount is None:
        max_amount = Decimal("200.00")
    if total_amount is None:
        total_amount = Decimal("1500.00")

    data = {
        "average_amount": average_amount,
        "std_dev_amount": std_dev_amount,
        "min_amount": min_amount,
        "max_amount": max_amount,
        "total_amount": total_amount,
        **kwargs,
    }

    return data


@factory_function(FrequencyMetrics)
def create_frequency_metrics_schema(
    average_days_between: float = 30.5,
    std_dev_days: float = 1.5,
    min_days: int = 29,
    max_days: int = 32,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid FrequencyMetrics schema instance.

    Args:
        average_days_between: Average number of days between payments
        std_dev_days: Standard deviation of days between payments
        min_days: Minimum days between payments
        max_days: Maximum days between payments
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create FrequencyMetrics schema
    """
    data = {
        "average_days_between": average_days_between,
        "std_dev_days": std_dev_days,
        "min_days": min_days,
        "max_days": max_days,
        **kwargs,
    }

    return data


@factory_function(SeasonalMetrics)
def create_seasonal_metrics_schema(
    avg_days_before_due: float = 3.5,
    std_dev_days: float = 1.2,
    sample_size: int = 10,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SeasonalMetrics schema instance.

    Args:
        avg_days_before_due: Average days before due date
        std_dev_days: Standard deviation of days before due date
        sample_size: Number of payments in this season
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SeasonalMetrics schema
    """
    data = {
        "avg_days_before_due": avg_days_before_due,
        "std_dev_days": std_dev_days,
        "sample_size": sample_size,
        **kwargs,
    }

    return data


@factory_function(PaymentPatternAnalysis)
def create_payment_pattern_analysis_schema(
    pattern_type: PatternType = PatternType.REGULAR,
    confidence_score: Decimal = Decimal("0.95"),
    frequency_metrics: Optional[Dict[str, Any]] = None,
    amount_statistics: Optional[Dict[str, Any]] = None,
    sample_size: int = 10,
    analysis_period_start: Optional[datetime] = None,
    analysis_period_end: Optional[datetime] = None,
    suggested_category: Optional[str] = None,
    notes: Optional[List[str]] = None,
    seasonal_metrics: Optional[Dict[int, Dict[str, Any]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentPatternAnalysis schema instance.

    Args:
        pattern_type: Type of payment pattern detected
        confidence_score: Confidence score between 0 and 1
        frequency_metrics: Metrics about payment frequency and timing
        amount_statistics: Statistical analysis of payment amounts
        sample_size: Number of payments analyzed
        analysis_period_start: Start date of the analysis period
        analysis_period_end: End date of the analysis period
        suggested_category: Suggested payment category based on pattern
        notes: Additional notes or observations about the pattern
        seasonal_metrics: Monthly or seasonal metrics, keyed by month number
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentPatternAnalysis schema
    """
    # Set default dates if not provided
    now = utc_now()
    if analysis_period_start is None:
        analysis_period_start = datetime(now.year - 1, 1, 1, tzinfo=now.tzinfo)
    if analysis_period_end is None:
        analysis_period_end = now

    # Create default nested objects if not provided
    if frequency_metrics is None:
        frequency_metrics = create_frequency_metrics_schema().model_dump()

    if amount_statistics is None:
        amount_statistics = create_amount_statistics_schema().model_dump()

    # Build the base data dictionary
    data = {
        "pattern_type": pattern_type,
        "confidence_score": confidence_score,
        "frequency_metrics": frequency_metrics,
        "amount_statistics": amount_statistics,
        "sample_size": sample_size,
        "analysis_period_start": analysis_period_start,
        "analysis_period_end": analysis_period_end,
        **kwargs,
    }

    # Add optional fields if provided
    if suggested_category is not None:
        data["suggested_category"] = suggested_category

    if notes is not None:
        data["notes"] = notes

    if seasonal_metrics is not None:
        data["seasonal_metrics"] = seasonal_metrics

    return data


@factory_function(PaymentPatternRequest)
def create_payment_pattern_request_schema(
    account_id: Optional[int] = None,
    category_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_sample_size: int = 3,
    liability_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentPatternRequest schema instance.

    Args:
        account_id: Optional account ID to filter payments
        category_id: Optional category ID to filter payments
        start_date: Optional start date for analysis period
        end_date: Optional end date for analysis period
        min_sample_size: Minimum number of payments required for analysis
        liability_id: Optional liability ID to filter payments
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentPatternRequest schema
    """
    data = {
        "min_sample_size": min_sample_size,
        **kwargs,
    }

    # Add optional fields if provided
    if account_id is not None:
        data["account_id"] = account_id

    if category_id is not None:
        data["category_id"] = category_id

    if start_date is not None:
        data["start_date"] = start_date

    if end_date is not None:
        data["end_date"] = end_date

    if liability_id is not None:
        data["liability_id"] = liability_id

    return data
