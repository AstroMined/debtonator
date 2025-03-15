from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest,
)
from src.schemas.realtime_cashflow import (
    AccountBalance,
    RealtimeCashflow,
    RealtimeCashflowResponse,
)
from src.schemas.recommendations import (
    BillPaymentTimingRecommendation,
    ConfidenceLevel,
    ImpactMetrics,
    RecommendationResponse,
    RecommendationType,
)


def test_realtime_cashflow_timezone_validation():
    # Test with naive datetime
    with pytest.raises(ValidationError) as exc_info:
        RealtimeCashflow(
            timestamp=datetime.now(),
            account_balances=[],
            total_available_funds=Decimal("0"),
            total_available_credit=Decimal("0"),
            total_liabilities_due=Decimal("0"),
            net_position=Decimal("0"),
            minimum_balance_required=Decimal("0"),
        )
    assert "Datetime must be timezone-aware" in str(exc_info.value)

    # Test with non-UTC timezone
    pst = ZoneInfo("America/Los_Angeles")
    with pytest.raises(ValidationError) as exc_info:
        RealtimeCashflow(
            timestamp=datetime.now(pst),
            account_balances=[],
            total_available_funds=Decimal("0"),
            total_available_credit=Decimal("0"),
            total_liabilities_due=Decimal("0"),
            net_position=Decimal("0"),
            minimum_balance_required=Decimal("0"),
        )
    assert "Datetime must be in UTC timezone" in str(exc_info.value)

    # Test with UTC timezone (should succeed)
    utc_now = datetime.now(ZoneInfo("UTC"))
    cashflow = RealtimeCashflow(
        timestamp=utc_now,
        account_balances=[],
        total_available_funds=Decimal("0"),
        total_available_credit=Decimal("0"),
        total_liabilities_due=Decimal("0"),
        net_position=Decimal("0"),
        minimum_balance_required=Decimal("0"),
    )
    assert cashflow.timestamp == utc_now


def test_cashflow_impact_timezone_validation():
    # Test with naive datetime
    with pytest.raises(ValidationError) as exc_info:
        CashflowImpact(
            date=datetime.now(),
            total_bills=Decimal("0"),
            available_funds=Decimal("0"),
        )
    assert "Datetime must be timezone-aware" in str(exc_info.value)

    # Test with non-UTC timezone
    pst = ZoneInfo("America/Los_Angeles")
    with pytest.raises(ValidationError) as exc_info:
        CashflowImpact(
            date=datetime.now(pst),
            total_bills=Decimal("0"),
            available_funds=Decimal("0"),
        )
    assert "Datetime must be in UTC timezone" in str(exc_info.value)

    # Test with UTC timezone (should succeed)
    utc_now = datetime.now(ZoneInfo("UTC"))
    impact = CashflowImpact(
        date=utc_now,
        total_bills=Decimal("0"),
        available_funds=Decimal("0"),
    )
    assert impact.date == utc_now


def test_split_impact_request_timezone_validation():
    # Test with naive datetime
    with pytest.raises(ValidationError) as exc_info:
        SplitImpactRequest(
            liability_id=1,
            splits=[],
            start_date=datetime.now(),
        )
    assert "Datetime must be timezone-aware" in str(exc_info.value)

    # Test with non-UTC timezone
    pst = ZoneInfo("America/Los_Angeles")
    with pytest.raises(ValidationError) as exc_info:
        SplitImpactRequest(
            liability_id=1,
            splits=[],
            start_date=datetime.now(pst),
        )
    assert "Datetime must be in UTC timezone" in str(exc_info.value)

    # Test with UTC timezone (should succeed)
    utc_now = datetime.now(ZoneInfo("UTC"))
    request = SplitImpactRequest(
        liability_id=1,
        splits=[],
        start_date=utc_now,
    )
    assert request.start_date == utc_now


def test_bill_payment_timing_recommendation_timezone_validation():
    utc_now = datetime.now(ZoneInfo("UTC"))
    metrics = ImpactMetrics(
        balance_impact=Decimal("0"),
        risk_score=Decimal("50"),
    )

    # Test with naive datetime
    with pytest.raises(ValidationError) as exc_info:
        BillPaymentTimingRecommendation(
            type=RecommendationType.BILL_PAYMENT_TIMING,
            confidence=ConfidenceLevel.HIGH,
            impact=metrics,
            bill_id=1,
            current_due_date=datetime.now(),
            recommended_date=utc_now,
            reason="Test",
            historical_pattern_strength=Decimal("0.8"),
            affected_accounts=[1],
        )
    assert "Datetime must be timezone-aware" in str(exc_info.value)

    # Test with non-UTC timezone
    pst = ZoneInfo("America/Los_Angeles")
    with pytest.raises(ValidationError) as exc_info:
        BillPaymentTimingRecommendation(
            type=RecommendationType.BILL_PAYMENT_TIMING,
            confidence=ConfidenceLevel.HIGH,
            impact=metrics,
            bill_id=1,
            current_due_date=datetime.now(pst),
            recommended_date=utc_now,
            reason="Test",
            historical_pattern_strength=Decimal("0.8"),
            affected_accounts=[1],
        )
    assert "Datetime must be in UTC timezone" in str(exc_info.value)

    # Test with UTC timezone (should succeed)
    recommendation = BillPaymentTimingRecommendation(
        type=RecommendationType.BILL_PAYMENT_TIMING,
        confidence=ConfidenceLevel.HIGH,
        impact=metrics,
        bill_id=1,
        current_due_date=utc_now,
        recommended_date=utc_now,
        reason="Test",
        historical_pattern_strength=Decimal("0.8"),
        affected_accounts=[1],
    )
    assert recommendation.current_due_date == utc_now
    assert recommendation.recommended_date == utc_now


def test_recommendation_response_timezone_validation():
    utc_now = datetime.now(ZoneInfo("UTC"))
    metrics = ImpactMetrics(
        balance_impact=Decimal("0"),
        risk_score=Decimal("50"),
    )
    recommendation = BillPaymentTimingRecommendation(
        type=RecommendationType.BILL_PAYMENT_TIMING,
        confidence=ConfidenceLevel.HIGH,
        impact=metrics,
        bill_id=1,
        current_due_date=utc_now,
        recommended_date=utc_now,
        reason="Test",
        historical_pattern_strength=Decimal("0.8"),
        affected_accounts=[1],
    )

    # Test with naive datetime
    with pytest.raises(ValidationError) as exc_info:
        RecommendationResponse(
            recommendations=[recommendation],
            total_savings_potential=Decimal("0"),
            average_confidence=Decimal("0.8"),
            generated_at=datetime.now(),
        )
    assert "Datetime must be timezone-aware" in str(exc_info.value)

    # Test with non-UTC timezone
    pst = ZoneInfo("America/Los_Angeles")
    with pytest.raises(ValidationError) as exc_info:
        RecommendationResponse(
            recommendations=[recommendation],
            total_savings_potential=Decimal("0"),
            average_confidence=Decimal("0.8"),
            generated_at=datetime.now(pst),
        )
    assert "Datetime must be in UTC timezone" in str(exc_info.value)

    # Test with UTC timezone (should succeed)
    response = RecommendationResponse(
        recommendations=[recommendation],
        total_savings_potential=Decimal("0"),
        average_confidence=Decimal("0.8"),
        generated_at=utc_now,
    )
    assert response.generated_at == utc_now
