"""
Unit tests for cashflow forecasting schema factory functions.

Tests ensure that cashflow forecasting schema factories produce valid schema instances
that pass validation and maintain ADR-011 compliance for datetime handling.
"""

# pylint: disable=no-member

from datetime import timedelta, timezone
from decimal import Decimal
from typing import List

from src.schemas.cashflow.cashflow_forecasting import (
    AccountForecastMetrics,
    AccountForecastRequest,
    AccountForecastResponse,
    AccountForecastResult,
    CustomForecastParameters,
    CustomForecastResponse,
    CustomForecastResult,
)
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import MEDIUM_AMOUNT
from tests.helpers.schema_factories.cashflow.cashflow_forecasting_schema_factories import (
    create_account_forecast_metrics_schema,
    create_account_forecast_request_schema,
    create_account_forecast_response_schema,
    create_account_forecast_result_schema,
    create_custom_forecast_parameters_schema,
    create_custom_forecast_response_schema,
    create_custom_forecast_result_schema,
)


def test_create_custom_forecast_parameters_schema():
    """Test creating a CustomForecastParameters schema with default values."""
    schema = create_custom_forecast_parameters_schema()

    assert isinstance(schema, CustomForecastParameters)

    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.start_date.tzinfo is not None
    assert schema.start_date.tzinfo == timezone.utc
    assert schema.end_date.tzinfo is not None
    assert schema.end_date.tzinfo == timezone.utc

    # Verify end_date is 90 days after start_date
    delta = schema.end_date - schema.start_date
    assert delta.days == 90

    assert schema.include_pending is True
    assert schema.confidence_threshold == Decimal("0.8")
    assert schema.include_recurring is True
    assert schema.include_historical_patterns is True
    assert schema.account_ids is None
    assert schema.categories is None


def test_create_custom_forecast_parameters_schema_with_custom_values():
    """Test creating a CustomForecastParameters schema with custom values."""
    start_date = utc_now()
    end_date = start_date + timedelta(days=30)
    account_ids = [1, 2, 3]
    categories = ["Utilities", "Rent", "Groceries"]

    schema = create_custom_forecast_parameters_schema(
        start_date=start_date,
        end_date=end_date,
        include_pending=False,
        account_ids=account_ids,
        categories=categories,
        confidence_threshold=Decimal("0.7"),
        include_recurring=False,
        include_historical_patterns=False,
    )

    assert isinstance(schema, CustomForecastParameters)

    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)
    assert datetime_equals(schema.end_date, end_date)

    assert schema.include_pending is False
    assert schema.account_ids == account_ids
    assert schema.categories == categories
    assert schema.confidence_threshold == Decimal("0.7")
    assert schema.include_recurring is False
    assert schema.include_historical_patterns is False


def test_create_custom_forecast_result_schema():
    """Test creating a CustomForecastResult schema with default values."""
    schema = create_custom_forecast_result_schema()

    assert isinstance(schema, CustomForecastResult)

    # Verify datetime field is timezone-aware and in UTC per ADR-011
    assert schema.date.tzinfo is not None
    assert schema.date.tzinfo == timezone.utc

    assert schema.projected_balance == MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    assert schema.projected_income == MEDIUM_AMOUNT * Decimal("2")  # 200.00
    assert schema.projected_expenses == MEDIUM_AMOUNT * Decimal("1.5")  # 150.00
    assert schema.confidence_score == Decimal("0.85")

    # Verify contributing factors and risk factors
    assert "Historical Patterns" in schema.contributing_factors
    assert "Timing Uncertainty" in schema.risk_factors
    assert sum(schema.contributing_factors.values()) == Decimal("1")
    assert sum(schema.risk_factors.values()) == Decimal("1")


def test_create_custom_forecast_result_schema_with_custom_values():
    """Test creating a CustomForecastResult schema with custom values."""
    date = utc_now()
    contributing_factors = {
        "Recurring Bills": Decimal("0.6"),
        "Upcoming Payments": Decimal("0.4"),
    }
    risk_factors = {
        "Low Balance": Decimal("0.7"),
        "Payment Delays": Decimal("0.3"),
    }

    schema = create_custom_forecast_result_schema(
        date=date,
        projected_balance=Decimal("2500.00"),
        projected_income=Decimal("500.00"),
        projected_expenses=Decimal("300.00"),
        confidence_score=Decimal("0.9"),
        contributing_factors=contributing_factors,
        risk_factors=risk_factors,
    )

    assert isinstance(schema, CustomForecastResult)

    # Verify datetime field using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.date, date)

    assert schema.projected_balance == Decimal("2500.00")
    assert schema.projected_income == Decimal("500.00")
    assert schema.projected_expenses == Decimal("300.00")
    assert schema.confidence_score == Decimal("0.9")

    # Verify custom contributing factors and risk factors
    assert schema.contributing_factors == contributing_factors
    assert schema.risk_factors == risk_factors
    assert sum(schema.contributing_factors.values()) == Decimal("1")
    assert sum(schema.risk_factors.values()) == Decimal("1")


def test_create_custom_forecast_response_schema():
    """Test creating a CustomForecastResponse schema with default values."""
    schema = create_custom_forecast_response_schema()

    assert isinstance(schema, CustomForecastResponse)

    # Verify parameters is a valid CustomForecastParameters instance
    assert isinstance(schema.parameters, CustomForecastParameters)

    # Verify results is a list of CustomForecastResult instances
    assert isinstance(schema.results, List)
    assert len(schema.results) == 5  # Default creates 5 results
    assert isinstance(schema.results[0], CustomForecastResult)

    # Verify timestamp is timezone-aware and in UTC per ADR-011
    assert schema.timestamp.tzinfo is not None
    assert schema.timestamp.tzinfo == timezone.utc

    assert schema.overall_confidence == Decimal("0.82")

    # Verify summary statistics
    assert "average_daily_balance" in schema.summary_statistics
    assert "minimum_balance" in schema.summary_statistics
    assert "maximum_balance" in schema.summary_statistics
    assert "total_income" in schema.summary_statistics
    assert "total_expenses" in schema.summary_statistics
    assert "net_change" in schema.summary_statistics


def test_create_custom_forecast_response_schema_with_custom_values():
    """Test creating a CustomForecastResponse schema with custom values."""
    timestamp = utc_now()
    parameters = create_custom_forecast_parameters_schema(
        include_pending=False, confidence_threshold=Decimal("0.6")
    ).model_dump()

    # Create custom results
    results = []
    base_date = utc_now()
    for i in range(3):  # Create 3 results instead of default 5
        result = create_custom_forecast_result_schema(
            date=base_date + timedelta(days=i),
            projected_balance=MEDIUM_AMOUNT * Decimal(20 + i),
            confidence_score=Decimal("0.75"),
        ).model_dump()
        results.append(result)

    summary_statistics = {
        "average_daily_balance": MEDIUM_AMOUNT * Decimal("25"),  # 2500.00
        "minimum_balance": MEDIUM_AMOUNT * Decimal("20"),  # 2000.00
        "maximum_balance": MEDIUM_AMOUNT * Decimal("30"),  # 3000.00
        "total_income": MEDIUM_AMOUNT * Decimal("15"),  # 1500.00
        "total_expenses": MEDIUM_AMOUNT * Decimal("8"),  # 800.00
        "net_change": MEDIUM_AMOUNT * Decimal("7"),  # 700.00
    }

    schema = create_custom_forecast_response_schema(
        parameters=parameters,
        results=results,
        overall_confidence=Decimal("0.78"),
        summary_statistics=summary_statistics,
        timestamp=timestamp,
    )

    assert isinstance(schema, CustomForecastResponse)

    # Verify custom parameters
    assert schema.parameters.include_pending is False
    assert schema.parameters.confidence_threshold == Decimal("0.6")

    # Verify custom results
    assert isinstance(schema.results, List)
    assert len(schema.results) == 3  # We specified 3 results
    for i, result in enumerate(schema.results):
        assert datetime_equals(result.date, base_date + timedelta(days=i))
        assert result.projected_balance == MEDIUM_AMOUNT * Decimal(20 + i)
        assert result.confidence_score == Decimal("0.75")

    # Verify timestamp using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.timestamp, timestamp)

    assert schema.overall_confidence == Decimal("0.78")

    # Verify custom summary statistics
    for key, value in summary_statistics.items():
        assert schema.summary_statistics[key] == value


def test_create_account_forecast_request_schema():
    """Test creating an AccountForecastRequest schema with default values."""
    account_id = 42
    schema = create_account_forecast_request_schema(account_id=account_id)

    assert isinstance(schema, AccountForecastRequest)
    assert schema.account_id == account_id

    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.start_date.tzinfo is not None
    assert schema.start_date.tzinfo == timezone.utc
    assert schema.end_date.tzinfo is not None
    assert schema.end_date.tzinfo == timezone.utc

    # Verify end_date is 90 days after start_date
    delta = schema.end_date - schema.start_date
    assert delta.days == 90

    assert schema.include_pending is True
    assert schema.include_recurring is True
    assert schema.include_transfers is True
    assert schema.confidence_threshold == Decimal("0.8")


def test_create_account_forecast_request_schema_with_custom_values():
    """Test creating an AccountForecastRequest schema with custom values."""
    account_id = 42
    start_date = utc_now()
    end_date = start_date + timedelta(days=30)

    schema = create_account_forecast_request_schema(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        include_pending=False,
        include_recurring=False,
        include_transfers=False,
        confidence_threshold=Decimal("0.7"),
    )

    assert isinstance(schema, AccountForecastRequest)
    assert schema.account_id == account_id

    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)
    assert datetime_equals(schema.end_date, end_date)

    assert schema.include_pending is False
    assert schema.include_recurring is False
    assert schema.include_transfers is False
    assert schema.confidence_threshold == Decimal("0.7")


def test_create_account_forecast_metrics_schema():
    """Test creating an AccountForecastMetrics schema with default values."""
    schema = create_account_forecast_metrics_schema()

    assert isinstance(schema, AccountForecastMetrics)

    assert schema.average_daily_balance == MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    assert schema.minimum_projected_balance == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.maximum_projected_balance == MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    assert schema.average_inflow == MEDIUM_AMOUNT  # 100.00
    assert schema.average_outflow == MEDIUM_AMOUNT * Decimal("0.8")  # 80.00
    assert schema.balance_volatility == MEDIUM_AMOUNT * Decimal("3")  # 300.00
    assert schema.forecast_confidence == Decimal("0.85")
    assert schema.credit_utilization is None

    # Verify projected_low_balance_dates are timezone-aware UTC datetimes per ADR-011
    assert len(schema.projected_low_balance_dates) == 3
    for date in schema.projected_low_balance_dates:
        assert date.tzinfo is not None
        assert date.tzinfo == timezone.utc


def test_create_account_forecast_metrics_schema_with_custom_values():
    """Test creating an AccountForecastMetrics schema with custom values."""
    now = utc_now()
    projected_low_balance_dates = [
        now + timedelta(days=5),
        now + timedelta(days=15),
        now + timedelta(days=25),
    ]

    schema = create_account_forecast_metrics_schema(
        average_daily_balance=Decimal("2500.00"),
        minimum_projected_balance=Decimal("1500.00"),
        maximum_projected_balance=Decimal("3500.00"),
        average_inflow=Decimal("200.00"),
        average_outflow=Decimal("150.00"),
        projected_low_balance_dates=projected_low_balance_dates,
        credit_utilization=Decimal("0.3"),
        balance_volatility=Decimal("450.00"),
        forecast_confidence=Decimal("0.9"),
    )

    assert isinstance(schema, AccountForecastMetrics)

    assert schema.average_daily_balance == Decimal("2500.00")
    assert schema.minimum_projected_balance == Decimal("1500.00")
    assert schema.maximum_projected_balance == Decimal("3500.00")
    assert schema.average_inflow == Decimal("200.00")
    assert schema.average_outflow == Decimal("150.00")
    assert schema.balance_volatility == Decimal("450.00")
    assert schema.forecast_confidence == Decimal("0.9")
    assert schema.credit_utilization == Decimal("0.3")

    # Verify projected_low_balance_dates using datetime_equals for proper ADR-011 comparison
    assert len(schema.projected_low_balance_dates) == 3
    for i, date in enumerate(schema.projected_low_balance_dates):
        assert datetime_equals(date, projected_low_balance_dates[i])


def test_create_account_forecast_result_schema():
    """Test creating an AccountForecastResult schema with default values."""
    schema = create_account_forecast_result_schema()

    assert isinstance(schema, AccountForecastResult)

    # Verify date is timezone-aware and in UTC per ADR-011
    assert schema.date.tzinfo is not None
    assert schema.date.tzinfo == timezone.utc

    assert schema.projected_balance == MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    assert schema.projected_inflow == MEDIUM_AMOUNT  # 100.00
    assert schema.projected_outflow == MEDIUM_AMOUNT * Decimal("0.8")  # 80.00
    assert schema.confidence_score == Decimal("0.85")

    # Verify contributing_transactions
    assert len(schema.contributing_transactions) == 3
    assert schema.contributing_transactions[0]["description"] == "Salary Deposit"
    assert schema.contributing_transactions[0]["type"] == "income"

    # Verify warning_flags is an empty list
    assert schema.warning_flags == []


def test_create_account_forecast_result_schema_with_custom_values():
    """Test creating an AccountForecastResult schema with custom values."""
    date = utc_now()
    contributing_transactions = [
        {
            "description": "Bonus Payment",
            "amount": MEDIUM_AMOUNT * Decimal("20"),  # 2000.00
            "type": "income",
        },
        {
            "description": "Mortgage Payment",
            "amount": MEDIUM_AMOUNT * Decimal("12"),  # 1200.00
            "type": "expense",
        },
    ]
    warning_flags = ["Low Balance Warning", "High Expense Alert"]

    schema = create_account_forecast_result_schema(
        date=date,
        projected_balance=Decimal("3000.00"),
        projected_inflow=Decimal("2000.00"),
        projected_outflow=Decimal("1200.00"),
        confidence_score=Decimal("0.95"),
        contributing_transactions=contributing_transactions,
        warning_flags=warning_flags,
    )

    assert isinstance(schema, AccountForecastResult)

    # Verify date using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.date, date)

    assert schema.projected_balance == Decimal("3000.00")
    assert schema.projected_inflow == Decimal("2000.00")
    assert schema.projected_outflow == Decimal("1200.00")
    assert schema.confidence_score == Decimal("0.95")

    # Verify custom contributing_transactions
    assert len(schema.contributing_transactions) == 2
    assert schema.contributing_transactions[0]["description"] == "Bonus Payment"
    assert schema.contributing_transactions[0]["amount"] == MEDIUM_AMOUNT * Decimal(
        "20"
    )
    assert schema.contributing_transactions[0]["type"] == "income"
    assert schema.contributing_transactions[1]["description"] == "Mortgage Payment"

    # Verify custom warning_flags
    assert schema.warning_flags == warning_flags


def test_create_account_forecast_response_schema():
    """Test creating an AccountForecastResponse schema with default values."""
    account_id = 42
    schema = create_account_forecast_response_schema(account_id=account_id)

    assert isinstance(schema, AccountForecastResponse)
    assert schema.account_id == account_id

    # Verify forecast_period is a tuple of two timezone-aware UTC datetimes per ADR-011
    assert isinstance(schema.forecast_period, tuple)
    assert len(schema.forecast_period) == 2
    assert schema.forecast_period[0].tzinfo is not None
    assert schema.forecast_period[0].tzinfo == timezone.utc
    assert schema.forecast_period[1].tzinfo is not None
    assert schema.forecast_period[1].tzinfo == timezone.utc

    # Verify metrics is an AccountForecastMetrics instance
    assert isinstance(schema.metrics, AccountForecastMetrics)

    # Verify daily_forecasts is a list of AccountForecastResult instances
    assert isinstance(schema.daily_forecasts, List)
    assert len(schema.daily_forecasts) == 5  # Default creates 5 results
    assert isinstance(schema.daily_forecasts[0], AccountForecastResult)

    # Verify timestamp is timezone-aware and in UTC per ADR-011
    assert schema.timestamp.tzinfo is not None
    assert schema.timestamp.tzinfo == timezone.utc

    assert schema.overall_confidence == Decimal("0.82")


def test_create_account_forecast_response_schema_with_custom_values():
    """Test creating an AccountForecastResponse schema with custom values."""
    account_id = 42
    now = utc_now()
    forecast_period = (now, now + timedelta(days=30))
    timestamp = now

    # Create custom metrics
    metrics = create_account_forecast_metrics_schema(
        average_daily_balance=Decimal("2500.00"), forecast_confidence=Decimal("0.9")
    ).model_dump()

    # Create custom daily forecasts
    daily_forecasts = []
    for i in range(3):  # Create 3 results instead of default 5
        forecast = create_account_forecast_result_schema(
            date=now + timedelta(days=i),
            projected_balance=MEDIUM_AMOUNT * Decimal(20 + i),
            confidence_score=Decimal("0.88"),
        ).model_dump()
        daily_forecasts.append(forecast)

    schema = create_account_forecast_response_schema(
        account_id=account_id,
        forecast_period=forecast_period,
        metrics=metrics,
        daily_forecasts=daily_forecasts,
        overall_confidence=Decimal("0.85"),
        timestamp=timestamp,
    )

    assert isinstance(schema, AccountForecastResponse)
    assert schema.account_id == account_id

    # Verify forecast_period using datetime_equals for proper ADR-011 comparison
    assert isinstance(schema.forecast_period, tuple)
    assert len(schema.forecast_period) == 2
    assert datetime_equals(schema.forecast_period[0], forecast_period[0])
    assert datetime_equals(schema.forecast_period[1], forecast_period[1])

    # Verify custom metrics
    assert schema.metrics.average_daily_balance == Decimal("2500.00")
    assert schema.metrics.forecast_confidence == Decimal("0.9")

    # Verify custom daily_forecasts
    assert isinstance(schema.daily_forecasts, List)
    assert len(schema.daily_forecasts) == 3
    for i, forecast in enumerate(schema.daily_forecasts):
        assert datetime_equals(forecast.date, now + timedelta(days=i))
        assert forecast.projected_balance == MEDIUM_AMOUNT * Decimal(20 + i)
        assert forecast.confidence_score == Decimal("0.88")

    # Verify timestamp using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.timestamp, timestamp)

    assert schema.overall_confidence == Decimal("0.85")
