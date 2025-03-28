"""
Income trends schema factory functions.

This module provides factory functions for creating valid income trends
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.income_trends import (
    FrequencyType,
    IncomePattern,
    IncomeTrendsAnalysis,
    IncomeTrendsRequest,
    PeriodType,
    SeasonalityMetrics,
    SourceStatistics,
)
from tests.helpers.schema_factories.base import (
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
    factory_function,
    utc_now,
)


@factory_function(IncomePattern)
def create_income_pattern_schema(
    source: str = "Salary",
    frequency: FrequencyType = FrequencyType.BIWEEKLY,
    average_amount: Optional[Decimal] = None,
    confidence_score: Optional[Decimal] = None,
    last_occurrence: Optional[datetime] = None,
    next_predicted: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomePattern schema instance.

    Args:
        source: Source of the income (e.g., employer name)
        frequency: Frequency pattern of the income
        average_amount: Average amount of income (defaults to 2000.00)
        confidence_score: Confidence score (0-1 scale, defaults to 0.85)
        last_occurrence: Date of the last occurrence (defaults to current UTC time)
        next_predicted: Predicted date of the next occurrence
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomePattern schema
    """
    if average_amount is None:
        average_amount = MEDIUM_AMOUNT * Decimal("20")  # 2000.00

    if confidence_score is None:
        confidence_score = Decimal("0.85")

    if last_occurrence is None:
        last_occurrence = utc_now()

    data = {
        "source": source,
        "frequency": frequency,
        "average_amount": average_amount,
        "confidence_score": confidence_score,
        "last_occurrence": last_occurrence,
        **kwargs,
    }

    if next_predicted is None and frequency != FrequencyType.IRREGULAR:
        # Estimate next occurrence based on frequency
        if frequency == FrequencyType.WEEKLY:
            next_predicted = last_occurrence + timedelta(days=7)
        elif frequency == FrequencyType.BIWEEKLY:
            next_predicted = last_occurrence + timedelta(days=14)
        elif frequency == FrequencyType.MONTHLY:
            # Approximate month as 30 days
            next_predicted = last_occurrence + timedelta(days=30)

    if next_predicted is not None:
        data["next_predicted"] = next_predicted

    return data


@factory_function(SeasonalityMetrics)
def create_seasonality_metrics_schema(
    period: PeriodType = PeriodType.MONTHLY,
    peak_months: Optional[List[int]] = None,
    trough_months: Optional[List[int]] = None,
    variance_coefficient: float = 0.35,
    confidence_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SeasonalityMetrics schema instance.

    Args:
        period: Period type for seasonality analysis
        peak_months: Months with peak income (defaults to [3, 11, 12])
        trough_months: Months with lowest income (defaults to [1, 7, 8])
        variance_coefficient: Coefficient of variance (defaults to 0.35)
        confidence_score: Confidence score (0-1 scale, defaults to 0.75)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SeasonalityMetrics schema
    """
    if peak_months is None:
        peak_months = [3, 11, 12]  # March, November, December

    if trough_months is None:
        trough_months = [1, 7, 8]  # January, July, August

    if confidence_score is None:
        confidence_score = Decimal("0.75")

    data = {
        "period": period,
        "peak_months": peak_months,
        "trough_months": trough_months,
        "variance_coefficient": variance_coefficient,
        "confidence_score": confidence_score,
        **kwargs,
    }

    return data


@factory_function(SourceStatistics)
def create_source_statistics_schema(
    source: str = "Salary",
    total_occurrences: int = 24,
    total_amount: Optional[Decimal] = None,
    average_amount: Optional[Decimal] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    standard_deviation: float = 150.0,
    reliability_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SourceStatistics schema instance.

    Args:
        source: Source of the income (e.g., employer name)
        total_occurrences: Total number of occurrences
        total_amount: Total amount received (defaults to 48000.00)
        average_amount: Average amount per occurrence (defaults to 2000.00)
        min_amount: Minimum amount received (defaults to 1850.00)
        max_amount: Maximum amount received (defaults to 2200.00)
        standard_deviation: Standard deviation of amounts
        reliability_score: Reliability score (0-1 scale, defaults to 0.9)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SourceStatistics schema
    """
    if average_amount is None:
        average_amount = MEDIUM_AMOUNT * Decimal("20")  # 2000.00

    if total_amount is None:
        total_amount = average_amount * Decimal(total_occurrences)  # 48000.00

    if min_amount is None:
        min_amount = average_amount - MEDIUM_AMOUNT * Decimal("1.5")  # 1850.00

    if max_amount is None:
        max_amount = average_amount + MEDIUM_AMOUNT * Decimal("2")  # 2200.00

    if reliability_score is None:
        reliability_score = Decimal("0.9")

    data = {
        "source": source,
        "total_occurrences": total_occurrences,
        "total_amount": total_amount,
        "average_amount": average_amount,
        "min_amount": min_amount,
        "max_amount": max_amount,
        "standard_deviation": standard_deviation,
        "reliability_score": reliability_score,
        **kwargs,
    }

    return data


@factory_function(IncomeTrendsAnalysis)
def create_income_trends_analysis_schema(
    patterns: Optional[List[Dict[str, Any]]] = None,
    seasonality: Optional[Dict[str, Any]] = None,
    source_statistics: Optional[List[Dict[str, Any]]] = None,
    analysis_date: Optional[datetime] = None,
    data_start_date: Optional[datetime] = None,
    data_end_date: Optional[datetime] = None,
    overall_predictability_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomeTrendsAnalysis schema instance.

    Args:
        patterns: List of identified income patterns
        seasonality: Seasonal patterns if detected
        source_statistics: Statistical analysis per income source
        analysis_date: Date when analysis was performed (defaults to current UTC time)
        data_start_date: Start date of analyzed data (defaults to 2 years ago)
        data_end_date: End date of analyzed data (defaults to current UTC time)
        overall_predictability_score: Overall predictability score (defaults to 0.82)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomeTrendsAnalysis schema
    """
    now = utc_now()
    if analysis_date is None:
        analysis_date = now

    if data_end_date is None:
        data_end_date = now

    if data_start_date is None:
        data_start_date = now - timedelta(days=730)  # 2 years ago

    if patterns is None:
        # Create sample patterns
        patterns = [
            create_income_pattern_schema(
                source="Salary",
                frequency=FrequencyType.BIWEEKLY,
                average_amount=MEDIUM_AMOUNT * Decimal("20"),  # 2000.00
            ).model_dump(),
            create_income_pattern_schema(
                source="Freelance",
                frequency=FrequencyType.IRREGULAR,
                average_amount=MEDIUM_AMOUNT * Decimal("5"),  # 500.00
                confidence_score=Decimal("0.65"),
            ).model_dump(),
        ]

    if source_statistics is None:
        # Create sample source statistics
        source_statistics = [
            create_source_statistics_schema(
                source="Salary",
                total_occurrences=24,
                average_amount=MEDIUM_AMOUNT * Decimal("20"),  # 2000.00
            ).model_dump(),
            create_source_statistics_schema(
                source="Freelance",
                total_occurrences=8,
                average_amount=MEDIUM_AMOUNT * Decimal("5"),  # 500.00
                min_amount=MEDIUM_AMOUNT * Decimal("2"),  # 200.00
                max_amount=MEDIUM_AMOUNT * Decimal("10"),  # 1000.00
                standard_deviation=250.0,
                reliability_score=Decimal("0.6"),
            ).model_dump(),
        ]

    if overall_predictability_score is None:
        overall_predictability_score = Decimal("0.82")

    data = {
        "patterns": patterns,
        "source_statistics": source_statistics,
        "analysis_date": analysis_date,
        "data_start_date": data_start_date,
        "data_end_date": data_end_date,
        "overall_predictability_score": overall_predictability_score,
        **kwargs,
    }

    if seasonality is not None:
        data["seasonality"] = seasonality
    else:
        # Add seasonality in about 50% of cases for better test coverage
        import random

        if random.random() > 0.5:
            data["seasonality"] = create_seasonality_metrics_schema().model_dump()

    return data


@factory_function(IncomeTrendsRequest)
def create_income_trends_request_schema(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source: Optional[str] = None,
    min_confidence: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomeTrendsRequest schema instance.

    Args:
        start_date: Optional start date for analysis period
        end_date: Optional end date for analysis period
        source: Optional specific income source to analyze
        min_confidence: Minimum confidence score (defaults to 0.5)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomeTrendsRequest schema
    """
    data = {
        **kwargs,
    }

    if start_date is not None:
        data["start_date"] = start_date

    if end_date is not None:
        data["end_date"] = end_date

    if source is not None:
        data["source"] = source

    if min_confidence is not None:
        data["min_confidence"] = min_confidence
    else:
        data["min_confidence"] = Decimal("0.5")

    return data
