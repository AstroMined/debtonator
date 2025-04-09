"""
Recommendation schema factory functions.

This module provides factory functions for creating valid Recommendation-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.recommendations import (
    BillPaymentTimingRecommendation,
    ConfidenceLevel,
    ImpactMetrics,
    RecommendationResponse,
    RecommendationType,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
    factory_function,
)


@factory_function(ImpactMetrics)
def create_impact_metrics_schema(
    balance_impact: Optional[Decimal] = None,
    credit_utilization_impact: Optional[Decimal] = None,
    risk_score: Optional[Decimal] = None,
    savings_potential: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid ImpactMetrics schema instance.

    Args:
        balance_impact: Impact on account balance (defaults to -100.00)
        credit_utilization_impact: Impact on credit utilization (0-1 range)
        risk_score: Risk score (0-100 range, defaults to 30.0)
        savings_potential: Potential savings (defaults to 50.00 if provided)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create ImpactMetrics schema
    """
    if balance_impact is None:
        balance_impact = -MEDIUM_AMOUNT  # Negative by default for impact

    if risk_score is None:
        risk_score = Decimal("30.0")  # Middle-range risk score

    data = {
        "balance_impact": balance_impact,
        "risk_score": risk_score,
        **kwargs,
    }

    if credit_utilization_impact is not None:
        data["credit_utilization_impact"] = credit_utilization_impact

    if savings_potential is not None:
        data["savings_potential"] = savings_potential
    elif "savings_potential" not in kwargs:
        data["savings_potential"] = SMALL_AMOUNT * Decimal("5")  # Default savings

    return data


@factory_function(BillPaymentTimingRecommendation)
def create_bill_payment_timing_recommendation_schema(
    bill_id: int,
    affected_accounts: Optional[List[int]] = None,
    current_due_date: Optional[datetime] = None,
    recommended_date: Optional[datetime] = None,
    confidence: str = ConfidenceLevel.MEDIUM,
    historical_pattern_strength: Optional[Decimal] = None,
    reason: str = "Optimal payment timing based on historical patterns",
    impact: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BillPaymentTimingRecommendation schema instance.

    Args:
        bill_id: ID of the bill this recommendation relates to
        affected_accounts: IDs of accounts affected (defaults to [1])
        current_due_date: Current scheduled due date (defaults to now + 15 days)
        recommended_date: Recommended payment date (defaults to now + 10 days)
        confidence: Confidence level (high/medium/low, defaults to medium)
        historical_pattern_strength: Pattern strength (0-1, defaults to 0.75)
        reason: Explanation for the recommendation
        impact: Impact metrics (defaults to standard metrics if None)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillPaymentTimingRecommendation schema
    """
    now = utc_now()

    if current_due_date is None:
        # Default due date is 15 days from now
        current_due_date = datetime(
            now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo
        )
        current_due_date = current_due_date.replace(day=min(now.day + 15, 28))

    if recommended_date is None:
        # Default recommended date is 10 days from now (5 days before due)
        recommended_date = datetime(
            now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo
        )
        recommended_date = recommended_date.replace(day=min(now.day + 10, 28))

    if affected_accounts is None:
        affected_accounts = [1]  # Default to account ID 1

    if historical_pattern_strength is None:
        historical_pattern_strength = Decimal("0.75")  # Strong pattern by default

    if impact is None:
        impact = create_impact_metrics_schema()

    data = {
        "bill_id": bill_id,
        "affected_accounts": affected_accounts,
        "current_due_date": current_due_date,
        "recommended_date": recommended_date,
        "confidence": confidence,
        "historical_pattern_strength": historical_pattern_strength,
        "reason": reason,
        "type": RecommendationType.BILL_PAYMENT_TIMING,
        "impact": impact,
        **kwargs,
    }

    return data


@factory_function(RecommendationResponse)
def create_recommendation_response_schema(
    recommendations: Optional[List[BillPaymentTimingRecommendation]] = None,
    total_savings_potential: Optional[Decimal] = None,
    average_confidence: Optional[Decimal] = None,
    generated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecommendationResponse schema instance.

    Args:
        recommendations: List of recommendations (creates 2 if None)
        total_savings_potential: Total potential savings (calculated if None)
        average_confidence: Average confidence level (calculated if None)
        generated_at: Generation timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecommendationResponse schema
    """
    if generated_at is None:
        generated_at = utc_now()

    if recommendations is None:
        # Create two sample recommendations
        recommendations = [
            create_bill_payment_timing_recommendation_schema(bill_id=1),
            create_bill_payment_timing_recommendation_schema(
                bill_id=2,
                confidence=ConfidenceLevel.HIGH,
                historical_pattern_strength=Decimal("0.9"),
            ),
        ]

    if total_savings_potential is None:
        # Calculate total savings from recommendations
        total_savings_potential = sum(
            (
                r.impact.savings_potential
                for r in recommendations
                if r.impact and r.impact.savings_potential is not None
            ),
            Decimal("0.00"),
        )

    if average_confidence is None:
        # Map confidence levels to values
        confidence_values = {
            ConfidenceLevel.LOW: Decimal("0.3"),
            ConfidenceLevel.MEDIUM: Decimal("0.6"),
            ConfidenceLevel.HIGH: Decimal("0.9"),
        }

        # Calculate average confidence
        if recommendations:
            confidence_sum = sum(
                confidence_values[r.confidence] for r in recommendations
            )
            average_confidence = confidence_sum / Decimal(len(recommendations))
        else:
            average_confidence = Decimal("0.5")  # Default if no recommendations

    data = {
        "recommendations": recommendations,
        "total_savings_potential": total_savings_potential,
        "average_confidence": average_confidence,
        "generated_at": generated_at,
        **kwargs,
    }

    return data
