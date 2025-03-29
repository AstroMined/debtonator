from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.cashflow.forecasting import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)


# Test valid object creation
def test_custom_forecast_parameters_valid():
    """Test valid custom forecast parameters schema creation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    params = CustomForecastParameters(
        start_date=now,
        end_date=future,
        include_pending=True,
        account_ids=[1, 2, 3],
        categories=["Bills", "Groceries", "Utilities"],
        confidence_threshold=Decimal("0.85"),
        include_recurring=True,
        include_historical_patterns=True,
    )

    assert params.start_date == now
    assert params.end_date == future
    assert params.include_pending is True
    assert params.account_ids == [1, 2, 3]
    assert params.categories == ["Bills", "Groceries", "Utilities"]
    assert params.confidence_threshold == Decimal("0.85")
    assert params.include_recurring is True
    assert params.include_historical_patterns is True


def test_custom_forecast_parameters_defaults():
    """Test custom forecast parameters with default values"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    params = CustomForecastParameters(start_date=now, end_date=future)

    assert params.start_date == now
    assert params.end_date == future
    assert params.include_pending is True  # Default
    assert params.account_ids is None  # Default
    assert params.categories is None  # Default
    assert params.confidence_threshold == Decimal("0.8")  # Default
    assert params.include_recurring is True  # Default
    assert params.include_historical_patterns is True  # Default


def test_custom_forecast_result_valid():
    """Test valid custom forecast result schema creation"""
    now = datetime.now(timezone.utc)

    result = CustomForecastResult(
        date=now,
        projected_balance=Decimal("2500.00"),
        projected_income=Decimal("1000.00"),
        projected_expenses=Decimal("800.00"),
        confidence_score=Decimal("0.85"),
        contributing_factors={"Income": Decimal("0.6"), "Bills": Decimal("0.4")},
        risk_factors={
            "Unexpected Expenses": Decimal("0.3"),
            "Income Variability": Decimal("0.2"),
        },
    )

    assert result.date == now
    assert result.projected_balance == Decimal("2500.00")
    assert result.projected_income == Decimal("1000.00")
    assert result.projected_expenses == Decimal("800.00")
    assert result.confidence_score == Decimal("0.85")
    assert result.contributing_factors == {
        "Income": Decimal("0.6"),
        "Bills": Decimal("0.4"),
    }
    assert result.risk_factors == {
        "Unexpected Expenses": Decimal("0.3"),
        "Income Variability": Decimal("0.2"),
    }


def test_custom_forecast_response_valid():
    """Test valid custom forecast response schema creation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    params = CustomForecastParameters(
        start_date=now,
        end_date=future,
        include_pending=True,
        account_ids=[1, 2],
        confidence_threshold=Decimal("0.85"),
    )

    result1 = CustomForecastResult(
        date=now,
        projected_balance=Decimal("2500.00"),
        projected_income=Decimal("1000.00"),
        projected_expenses=Decimal("800.00"),
        confidence_score=Decimal("0.85"),
        contributing_factors={"Income": Decimal("0.6"), "Bills": Decimal("0.4")},
        risk_factors={"Unexpected Expenses": Decimal("0.3")},
    )

    result2 = CustomForecastResult(
        date=now + timedelta(days=1),
        projected_balance=Decimal("2700.00"),
        projected_income=Decimal("1000.00"),
        projected_expenses=Decimal("0.00"),
        confidence_score=Decimal("0.90"),
        contributing_factors={"Income": Decimal("1.0")},
        risk_factors={},
    )

    response = CustomForecastResponse(
        parameters=params,
        results=[result1, result2],
        overall_confidence=Decimal("0.88"),
        summary_statistics={
            "average_balance": Decimal("2600.00"),
            "total_income": Decimal("2000.00"),
            "total_expenses": Decimal("800.00"),
        },
        timestamp=now,
    )

    assert response.parameters == params
    assert len(response.results) == 2
    assert response.results[0].projected_balance == Decimal("2500.00")
    assert response.results[1].projected_balance == Decimal("2700.00")
    assert response.overall_confidence == Decimal("0.88")
    assert response.summary_statistics["average_balance"] == Decimal("2600.00")
    assert response.timestamp == now


def test_account_forecast_request_valid():
    """Test valid account forecast request schema creation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    request = AccountForecastRequest(
        account_id=1,
        start_date=now,
        end_date=future,
        include_pending=True,
        include_recurring=True,
        include_transfers=False,
        confidence_threshold=Decimal("0.75"),
    )

    assert request.account_id == 1
    assert request.start_date == now
    assert request.end_date == future
    assert request.include_pending is True
    assert request.include_recurring is True
    assert request.include_transfers is False
    assert request.confidence_threshold == Decimal("0.75")


def test_account_forecast_request_defaults():
    """Test account forecast request with default values"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    request = AccountForecastRequest(account_id=1, start_date=now, end_date=future)

    assert request.account_id == 1
    assert request.start_date == now
    assert request.end_date == future
    assert request.include_pending is True  # Default
    assert request.include_recurring is True  # Default
    assert request.include_transfers is True  # Default
    assert request.confidence_threshold == Decimal("0.8")  # Default


def test_account_forecast_metrics_valid():
    """Test valid account forecast metrics schema creation"""
    now = datetime.now(timezone.utc)
    future1 = now + timedelta(days=5)
    future2 = now + timedelta(days=15)

    metrics = AccountForecastMetrics(
        average_daily_balance=Decimal("2500.00"),
        minimum_projected_balance=Decimal("1800.00"),
        maximum_projected_balance=Decimal("3200.00"),
        average_inflow=Decimal("1000.00"),
        average_outflow=Decimal("900.00"),
        projected_low_balance_dates=[future1, future2],
        credit_utilization=Decimal("0.65"),
        balance_volatility=Decimal("350.75"),
        forecast_confidence=Decimal("0.85"),
    )

    assert metrics.average_daily_balance == Decimal("2500.00")
    assert metrics.minimum_projected_balance == Decimal("1800.00")
    assert metrics.maximum_projected_balance == Decimal("3200.00")
    assert metrics.average_inflow == Decimal("1000.00")
    assert metrics.average_outflow == Decimal("900.00")
    assert metrics.projected_low_balance_dates == [future1, future2]
    assert metrics.credit_utilization == Decimal("0.65")
    assert metrics.balance_volatility == Decimal("350.75")
    assert metrics.forecast_confidence == Decimal("0.85")


def test_account_forecast_metrics_optional_fields():
    """Test account forecast metrics with optional fields"""
    now = datetime.now(timezone.utc)

    # Test without credit_utilization (optional field)
    metrics = AccountForecastMetrics(
        average_daily_balance=Decimal("2500.00"),
        minimum_projected_balance=Decimal("1800.00"),
        maximum_projected_balance=Decimal("3200.00"),
        average_inflow=Decimal("1000.00"),
        average_outflow=Decimal("900.00"),
        projected_low_balance_dates=[now + timedelta(days=5)],
        balance_volatility=Decimal("350.75"),
        forecast_confidence=Decimal("0.85"),
    )

    assert metrics.credit_utilization is None


def test_account_forecast_result_valid():
    """Test valid account forecast result schema creation"""
    now = datetime.now(timezone.utc)

    result = AccountForecastResult(
        date=now,
        projected_balance=Decimal("2500.00"),
        projected_inflow=Decimal("1000.00"),
        projected_outflow=Decimal("800.00"),
        confidence_score=Decimal("0.85"),
        contributing_transactions=[
            {
                "amount": Decimal("500.00"),
                "category": "Salary",
                "confidence": Decimal("0.95"),
            },
            {
                "amount": Decimal("-300.00"),
                "category": "Bills",
                "confidence": Decimal("0.90"),
            },
        ],
        warning_flags=["Low Balance Risk"],
    )

    assert result.date == now
    assert result.projected_balance == Decimal("2500.00")
    assert result.projected_inflow == Decimal("1000.00")
    assert result.projected_outflow == Decimal("800.00")
    assert result.confidence_score == Decimal("0.85")
    assert len(result.contributing_transactions) == 2
    assert result.contributing_transactions[0]["amount"] == Decimal("500.00")
    assert result.warning_flags == ["Low Balance Risk"]


def test_account_forecast_result_default_warnings():
    """Test account forecast result with default warnings"""
    now = datetime.now(timezone.utc)

    result = AccountForecastResult(
        date=now,
        projected_balance=Decimal("2500.00"),
        projected_inflow=Decimal("1000.00"),
        projected_outflow=Decimal("800.00"),
        confidence_score=Decimal("0.85"),
        contributing_transactions=[],
    )

    assert result.warning_flags == []  # Default is empty list


def test_account_forecast_response_valid():
    """Test valid account forecast response schema creation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    metrics = AccountForecastMetrics(
        average_daily_balance=Decimal("2500.00"),
        minimum_projected_balance=Decimal("1800.00"),
        maximum_projected_balance=Decimal("3200.00"),
        average_inflow=Decimal("1000.00"),
        average_outflow=Decimal("900.00"),
        projected_low_balance_dates=[now + timedelta(days=5)],
        credit_utilization=Decimal("0.65"),
        balance_volatility=Decimal("350.75"),
        forecast_confidence=Decimal("0.85"),
    )

    result1 = AccountForecastResult(
        date=now,
        projected_balance=Decimal("2500.00"),
        projected_inflow=Decimal("1000.00"),
        projected_outflow=Decimal("800.00"),
        confidence_score=Decimal("0.85"),
        contributing_transactions=[{"amount": Decimal("500.00"), "category": "Salary"}],
    )

    result2 = AccountForecastResult(
        date=now + timedelta(days=1),
        projected_balance=Decimal("2700.00"),
        projected_inflow=Decimal("0.00"),
        projected_outflow=Decimal("0.00"),
        confidence_score=Decimal("0.90"),
        contributing_transactions=[],
    )

    response = AccountForecastResponse(
        account_id=1,
        forecast_period=(now, future),
        metrics=metrics,
        daily_forecasts=[result1, result2],
        overall_confidence=Decimal("0.88"),
        timestamp=now,
    )

    assert response.account_id == 1
    assert response.forecast_period == (now, future)
    assert response.metrics == metrics
    assert len(response.daily_forecasts) == 2
    assert response.daily_forecasts[0].date == now
    assert response.overall_confidence == Decimal("0.88")
    assert response.timestamp == now


# Test field validations
def test_confidence_threshold_range():
    """Test confidence threshold range validation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    # Test below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        CustomForecastParameters(
            start_date=now,
            end_date=future,
            confidence_threshold=Decimal("-0.1"),  # Below minimum
        )

    # Test above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        CustomForecastParameters(
            start_date=now,
            end_date=future,
            confidence_threshold=Decimal("1.1"),  # Above maximum
        )

    # Test below minimum in AccountForecastRequest
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountForecastRequest(
            account_id=1,
            start_date=now,
            end_date=future,
            confidence_threshold=Decimal("-0.1"),  # Below minimum
        )

    # Test above maximum in AccountForecastRequest
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountForecastRequest(
            account_id=1,
            start_date=now,
            end_date=future,
            confidence_threshold=Decimal("1.1"),  # Above maximum
        )


def test_confidence_score_range():
    """Test confidence score range validation"""
    now = datetime.now(timezone.utc)

    # Test below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        CustomForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_income=Decimal("1000.00"),
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("-0.1"),  # Below minimum
            contributing_factors={},
            risk_factors={},
        )

    # Test above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        CustomForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_income=Decimal("1000.00"),
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("1.1"),  # Above maximum
            contributing_factors={},
            risk_factors={},
        )

    # Test below minimum in AccountForecastResult
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_inflow=Decimal("1000.00"),
            projected_outflow=Decimal("800.00"),
            confidence_score=Decimal("-0.1"),  # Below minimum
            contributing_transactions=[],
        )

    # Test above maximum in AccountForecastResult
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_inflow=Decimal("1000.00"),
            projected_outflow=Decimal("800.00"),
            confidence_score=Decimal("1.1"),  # Above maximum
            contributing_transactions=[],
        )


def test_credit_utilization_range():
    """Test credit utilization range validation"""
    now = datetime.now(timezone.utc)

    # Test below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountForecastMetrics(
            average_daily_balance=Decimal("2500.00"),
            minimum_projected_balance=Decimal("1800.00"),
            maximum_projected_balance=Decimal("3200.00"),
            average_inflow=Decimal("1000.00"),
            average_outflow=Decimal("900.00"),
            projected_low_balance_dates=[now],
            credit_utilization=Decimal("-0.1"),  # Below minimum
            balance_volatility=Decimal("350.75"),
            forecast_confidence=Decimal("0.85"),
        )

    # Test above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountForecastMetrics(
            average_daily_balance=Decimal("2500.00"),
            minimum_projected_balance=Decimal("1800.00"),
            maximum_projected_balance=Decimal("3200.00"),
            average_inflow=Decimal("1000.00"),
            average_outflow=Decimal("900.00"),
            projected_low_balance_dates=[now],
            credit_utilization=Decimal("1.1"),  # Above maximum
            balance_volatility=Decimal("350.75"),
            forecast_confidence=Decimal("0.85"),
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    # Test too many decimal places in confidence_threshold
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        CustomForecastParameters(
            start_date=now,
            end_date=future,
            confidence_threshold=Decimal("0.80001"),  # Too many decimal places
        )

    # Test too many decimal places in projected_balance
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        CustomForecastResult(
            date=now,
            projected_balance=Decimal("2500.123"),  # Too many decimal places
            projected_income=Decimal("1000.00"),
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("0.85"),
            contributing_factors={},
            risk_factors={},
        )

    # Test too many decimal places in projected_income
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        CustomForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_income=Decimal("1000.123"),  # Too many decimal places
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("0.85"),
            contributing_factors={},
            risk_factors={},
        )


def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    # Test naive datetime in start_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CustomForecastParameters(
            start_date=datetime.now(), end_date=future  # Naive datetime
        )

    # Test non-UTC timezone in end_date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CustomForecastParameters(
            start_date=now,
            end_date=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )

    # Test naive datetime in date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CustomForecastResult(
            date=datetime.now(),  # Naive datetime
            projected_balance=Decimal("2500.00"),
            projected_income=Decimal("1000.00"),
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("0.85"),
            contributing_factors={},
            risk_factors={},
        )

    # Test non-UTC timezone in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CustomForecastResponse(
            parameters=CustomForecastParameters(start_date=now, end_date=future),
            results=[],
            overall_confidence=Decimal("0.85"),
            summary_statistics={},
            timestamp=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )


def test_required_fields():
    """Test required fields validation"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=30)

    # Test missing start_date in CustomForecastParameters
    with pytest.raises(ValidationError, match="Field required"):
        CustomForecastParameters(end_date=future)

    # Test missing end_date in CustomForecastParameters
    with pytest.raises(ValidationError, match="Field required"):
        CustomForecastParameters(start_date=now)

    # Test missing date in CustomForecastResult
    with pytest.raises(ValidationError, match="Field required"):
        CustomForecastResult(
            projected_balance=Decimal("2500.00"),
            projected_income=Decimal("1000.00"),
            projected_expenses=Decimal("800.00"),
            confidence_score=Decimal("0.85"),
            contributing_factors={},
            risk_factors={},
        )

    # Test missing account_id in AccountForecastRequest
    with pytest.raises(ValidationError, match="Field required"):
        AccountForecastRequest(start_date=now, end_date=future)

    # Test missing projected_inflow in AccountForecastResult
    with pytest.raises(ValidationError, match="Field required"):
        AccountForecastResult(
            date=now,
            projected_balance=Decimal("2500.00"),
            projected_outflow=Decimal("800.00"),
            confidence_score=Decimal("0.85"),
            contributing_transactions=[],
        )
