"""
Unit tests for cashflow metrics schema factory functions.

Tests ensure that cashflow metrics schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal

from src.schemas.cashflow.cashflow_metrics import (
    DeficitCalculation,
    HourlyRates,
    MinimumRequired,
)
from tests.helpers.schema_factories.cashflow.cashflow_metrics_schema_factories import (
    create_deficit_calculation_schema,
    create_hourly_rates_schema,
    create_minimum_required_schema,
)


def test_create_minimum_required_schema():
    """Test creating a MinimumRequired schema with default values."""
    schema = create_minimum_required_schema()

    assert isinstance(schema, MinimumRequired)
    assert schema.min_14_day == Decimal("500.00")
    assert schema.min_30_day == Decimal("1000.00")
    assert schema.min_60_day == Decimal("2000.00")
    assert schema.min_90_day == Decimal("3000.00")


def test_create_minimum_required_schema_with_custom_values():
    """Test creating a MinimumRequired schema with custom values."""
    schema = create_minimum_required_schema(
        min_14_day=Decimal("750.00"),
        min_30_day=Decimal("1500.00"),
        min_60_day=Decimal("3000.00"),
        min_90_day=Decimal("4500.00"),
    )

    assert isinstance(schema, MinimumRequired)
    assert schema.min_14_day == Decimal("750.00")
    assert schema.min_30_day == Decimal("1500.00")
    assert schema.min_60_day == Decimal("3000.00")
    assert schema.min_90_day == Decimal("4500.00")


def test_create_minimum_required_schema_with_partial_custom_values():
    """Test creating a MinimumRequired schema with some custom values."""
    schema = create_minimum_required_schema(
        min_14_day=Decimal("600.00"), min_60_day=Decimal("2500.00")
    )

    assert isinstance(schema, MinimumRequired)
    assert schema.min_14_day == Decimal("600.00")
    assert schema.min_30_day == Decimal("1000.00")  # Default value
    assert schema.min_60_day == Decimal("2500.00")
    assert schema.min_90_day == Decimal("3000.00")  # Default value


def test_create_deficit_calculation_schema():
    """Test creating a DeficitCalculation schema with default values."""
    schema = create_deficit_calculation_schema()

    assert isinstance(schema, DeficitCalculation)
    assert schema.daily_deficit == Decimal("25.00")
    assert schema.yearly_deficit == Decimal("9125.00")
    assert schema.required_income == Decimal("12000.00")


def test_create_deficit_calculation_schema_with_custom_values():
    """Test creating a DeficitCalculation schema with custom values."""
    schema = create_deficit_calculation_schema(
        daily_deficit=Decimal("40.00"),
        yearly_deficit=Decimal("14600.00"),
        required_income=Decimal("20000.00"),
    )

    assert isinstance(schema, DeficitCalculation)
    assert schema.daily_deficit == Decimal("40.00")
    assert schema.yearly_deficit == Decimal("14600.00")
    assert schema.required_income == Decimal("20000.00")


def test_create_deficit_calculation_schema_auto_yearly_calculation():
    """Test that yearly deficit is calculated from daily deficit if not provided."""
    schema = create_deficit_calculation_schema(
        daily_deficit=Decimal("30.00"), required_income=Decimal("15000.00")
    )

    assert isinstance(schema, DeficitCalculation)
    assert schema.daily_deficit == Decimal("30.00")

    # Yearly deficit should be daily_deficit * 365
    expected_yearly = Decimal("30.00") * Decimal("365")
    assert schema.yearly_deficit == expected_yearly

    assert schema.required_income == Decimal("15000.00")


def test_create_hourly_rates_schema():
    """Test creating an HourlyRates schema with default values."""
    schema = create_hourly_rates_schema()

    assert isinstance(schema, HourlyRates)
    assert schema.hourly_rate_40 == Decimal("20.00")
    assert schema.hourly_rate_30 == Decimal("26.67")
    assert schema.hourly_rate_20 == Decimal("40.00")


def test_create_hourly_rates_schema_with_custom_values():
    """Test creating an HourlyRates schema with custom values."""
    schema = create_hourly_rates_schema(
        hourly_rate_40=Decimal("25.00"),
        hourly_rate_30=Decimal("33.33"),
        hourly_rate_20=Decimal("50.00"),
    )

    assert isinstance(schema, HourlyRates)
    assert schema.hourly_rate_40 == Decimal("25.00")
    assert schema.hourly_rate_30 == Decimal("33.33")
    assert schema.hourly_rate_20 == Decimal("50.00")


def test_create_hourly_rates_schema_with_partial_custom_values():
    """Test creating an HourlyRates schema with some custom values."""
    schema = create_hourly_rates_schema(hourly_rate_40=Decimal("30.00"))

    assert isinstance(schema, HourlyRates)
    assert schema.hourly_rate_40 == Decimal("30.00")
    assert schema.hourly_rate_30 == Decimal("26.67")  # Default value
    assert schema.hourly_rate_20 == Decimal("40.00")  # Default value
