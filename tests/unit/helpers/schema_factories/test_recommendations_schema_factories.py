"""
Unit tests for recommendation schema factory functions.

Tests ensure that recommendation schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

from src.schemas.recommendations import (
    BillPaymentTimingRecommendation,
    ConfidenceLevel,
    ImpactMetrics,
    RecommendationResponse,
    RecommendationType,
)
from tests.helpers.schema_factories.recommendations_schema_factories import (
    create_bill_payment_timing_recommendation_schema,
    create_impact_metrics_schema,
    create_recommendation_response_schema,
)


def test_create_impact_metrics_schema():
    """Test creating an ImpactMetrics schema with default values."""
    schema = create_impact_metrics_schema()

    assert isinstance(schema, ImpactMetrics)
    assert schema.balance_impact == Decimal("-100.00")
    assert schema.credit_utilization_impact is None
    assert schema.risk_score == Decimal("30.0")
    assert schema.savings_potential == Decimal("50.00")


def test_create_impact_metrics_schema_with_custom_values():
    """Test creating an ImpactMetrics schema with custom values."""
    schema = create_impact_metrics_schema(
        balance_impact=Decimal("-200.00"),
        credit_utilization_impact=Decimal("0.05"),
        risk_score=Decimal("45.0"),
        savings_potential=Decimal("75.00"),
    )

    assert isinstance(schema, ImpactMetrics)
    assert schema.balance_impact == Decimal("-200.00")
    assert schema.credit_utilization_impact == Decimal("0.05")
    assert schema.risk_score == Decimal("45.0")
    assert schema.savings_potential == Decimal("75.00")


def test_create_impact_metrics_schema_with_partial_custom_values():
    """Test creating an ImpactMetrics schema with some custom values."""
    schema = create_impact_metrics_schema(
        balance_impact=Decimal("-150.00"), credit_utilization_impact=Decimal("0.1")
    )

    assert isinstance(schema, ImpactMetrics)
    assert schema.balance_impact == Decimal("-150.00")
    assert schema.credit_utilization_impact == Decimal("0.1")
    assert schema.risk_score == Decimal("30.0")  # Default value
    assert schema.savings_potential == Decimal("50.00")  # Default value


def test_create_bill_payment_timing_recommendation_schema():
    """Test creating a BillPaymentTimingRecommendation schema with default values."""
    schema = create_bill_payment_timing_recommendation_schema(bill_id=1)

    assert isinstance(schema, BillPaymentTimingRecommendation)
    assert schema.bill_id == 1
    assert schema.type == RecommendationType.BILL_PAYMENT_TIMING
    assert schema.confidence == ConfidenceLevel.MEDIUM
    assert schema.historical_pattern_strength == Decimal("0.75")
    assert schema.affected_accounts == [1]
    assert isinstance(schema.current_due_date, datetime)
    assert isinstance(schema.recommended_date, datetime)
    assert schema.current_due_date.tzinfo == timezone.utc
    assert schema.recommended_date.tzinfo == timezone.utc
    assert (
        schema.current_due_date > schema.recommended_date
    )  # Due date is after recommended date
    assert isinstance(schema.impact, ImpactMetrics)
    assert schema.reason == "Optimal payment timing based on historical patterns"


def test_create_bill_payment_timing_recommendation_schema_with_custom_values():
    """Test creating a BillPaymentTimingRecommendation schema with custom values."""
    current_due_date = datetime(2023, 6, 20, tzinfo=timezone.utc)
    recommended_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
    affected_accounts = [2, 3]
    custom_impact = create_impact_metrics_schema(
        balance_impact=Decimal("-300.00"), savings_potential=Decimal("100.00")
    )

    schema = create_bill_payment_timing_recommendation_schema(
        bill_id=2,
        affected_accounts=affected_accounts,
        current_due_date=current_due_date,
        recommended_date=recommended_date,
        confidence=ConfidenceLevel.HIGH,
        historical_pattern_strength=Decimal("0.95"),
        reason="Pay early to avoid cash flow issues",
        impact=custom_impact,
    )

    assert isinstance(schema, BillPaymentTimingRecommendation)
    assert schema.bill_id == 2
    assert schema.type == RecommendationType.BILL_PAYMENT_TIMING
    assert schema.confidence == ConfidenceLevel.HIGH
    assert schema.historical_pattern_strength == Decimal("0.95")
    assert schema.affected_accounts == affected_accounts
    assert schema.current_due_date == current_due_date
    assert schema.recommended_date == recommended_date
    assert schema.impact.balance_impact == Decimal("-300.00")
    assert schema.impact.savings_potential == Decimal("100.00")
    assert schema.reason == "Pay early to avoid cash flow issues"


def test_create_recommendation_response_schema():
    """Test creating a RecommendationResponse schema with default values."""
    schema = create_recommendation_response_schema()

    assert isinstance(schema, RecommendationResponse)
    assert isinstance(schema.generated_at, datetime)
    assert schema.generated_at.tzinfo == timezone.utc
    assert len(schema.recommendations) == 2
    assert schema.recommendations[0].bill_id == 1
    assert schema.recommendations[1].bill_id == 2
    assert schema.recommendations[0].confidence == ConfidenceLevel.MEDIUM
    assert schema.recommendations[1].confidence == ConfidenceLevel.HIGH

    # Verify total savings potential is sum of individual savings potentials
    expected_savings = sum(
        r.impact.savings_potential
        for r in schema.recommendations
        if r.impact.savings_potential is not None
    )
    assert schema.total_savings_potential == expected_savings

    # Verify average confidence calculation
    confidence_values = {
        ConfidenceLevel.LOW: Decimal("0.3"),
        ConfidenceLevel.MEDIUM: Decimal("0.6"),
        ConfidenceLevel.HIGH: Decimal("0.9"),
    }
    expected_avg_confidence = (
        confidence_values[schema.recommendations[0].confidence]
        + confidence_values[schema.recommendations[1].confidence]
    ) / Decimal("2")
    assert schema.average_confidence == expected_avg_confidence


def test_create_recommendation_response_schema_with_custom_values():
    """Test creating a RecommendationResponse schema with custom values."""
    generated_at = datetime(2023, 6, 15, tzinfo=timezone.utc)

    recommendation1 = create_bill_payment_timing_recommendation_schema(
        bill_id=1, confidence=ConfidenceLevel.HIGH
    )

    recommendation2 = create_bill_payment_timing_recommendation_schema(
        bill_id=2, confidence=ConfidenceLevel.MEDIUM
    )

    recommendations = [recommendation1, recommendation2]

    schema = create_recommendation_response_schema(
        recommendations=recommendations,
        total_savings_potential=Decimal("150.00"),
        average_confidence=Decimal("0.75"),
        generated_at=generated_at,
    )

    assert isinstance(schema, RecommendationResponse)
    assert schema.generated_at == generated_at
    assert schema.recommendations == recommendations
    assert schema.total_savings_potential == Decimal("150.00")
    assert schema.average_confidence == Decimal("0.75")


def test_create_recommendation_response_schema_with_empty_recommendations():
    """Test that empty recommendations list is handled correctly."""
    schema = create_recommendation_response_schema(
        recommendations=[],
        total_savings_potential=Decimal("0.00"),
        average_confidence=Decimal("0.5"),
    )

    assert isinstance(schema, RecommendationResponse)
    assert len(schema.recommendations) == 0
    assert schema.total_savings_potential == Decimal("0.00")
    assert schema.average_confidence == Decimal("0.5")
