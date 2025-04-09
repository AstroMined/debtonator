"""
Unit tests for cashflow base schema factory functions.

Tests ensure that cashflow base schema factories produce valid schema instances
that pass validation and maintain ADR-011 compliance for datetime handling.
"""

# pylint: disable=no-member

from datetime import timezone
from decimal import Decimal

from src.schemas.cashflow.cashflow_base import (
    CashflowCreate,
    CashflowFilters,
    CashflowUpdate,
)
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
)
from tests.helpers.schema_factories.cashflow.base_schema_factories import (
    create_cashflow_filters_schema,
    create_cashflow_schema,
    create_cashflow_update_schema,
)


def test_create_cashflow_schema():
    """Test creating a CashflowCreate schema with default values."""
    schema = create_cashflow_schema()

    assert isinstance(schema, CashflowCreate)
    assert schema.total_bills == MEDIUM_AMOUNT  # 100.00
    assert schema.total_income == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.balance == MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    assert schema.forecast == MEDIUM_AMOUNT * Decimal("25")  # 2500.00
    assert schema.min_14_day == MEDIUM_AMOUNT * Decimal("5")  # 500.00
    assert schema.min_30_day == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.min_60_day == MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    assert schema.min_90_day == MEDIUM_AMOUNT * Decimal("30")  # 3000.00
    assert schema.daily_deficit == SMALL_AMOUNT * Decimal("2.5")  # 25.00
    assert schema.yearly_deficit == schema.daily_deficit * Decimal("365")  # ~9125.00
    assert schema.required_income == MEDIUM_AMOUNT * Decimal("120")  # 12000.00
    assert schema.hourly_rate_40 == SMALL_AMOUNT * Decimal("2")  # 20.00
    assert schema.hourly_rate_30 == Decimal("26.67")
    assert schema.hourly_rate_20 == SMALL_AMOUNT * Decimal("4")  # 40.00

    # Verify that the datetime is timezone-aware and in UTC per ADR-011
    assert schema.forecast_date.tzinfo is not None
    assert schema.forecast_date.tzinfo == timezone.utc


def test_create_cashflow_schema_with_custom_values():
    """Test creating a CashflowCreate schema with custom values."""
    now = utc_now()

    schema = create_cashflow_schema(
        total_bills=Decimal("200.00"),
        total_income=Decimal("3000.00"),
        balance=Decimal("2500.00"),
        forecast=Decimal("5000.00"),
        min_14_day=Decimal("800.00"),
        min_30_day=Decimal("1500.00"),
        min_60_day=Decimal("3000.00"),
        min_90_day=Decimal("5000.00"),
        daily_deficit=Decimal("35.00"),
        yearly_deficit=Decimal("12775.00"),
        required_income=Decimal("15000.00"),
        hourly_rate_40=Decimal("25.00"),
        hourly_rate_30=Decimal("33.33"),
        hourly_rate_20=Decimal("50.00"),
        forecast_date=now,
    )

    assert isinstance(schema, CashflowCreate)
    assert schema.total_bills == Decimal("200.00")
    assert schema.total_income == Decimal("3000.00")
    assert schema.balance == Decimal("2500.00")
    assert schema.forecast == Decimal("5000.00")
    assert schema.min_14_day == Decimal("800.00")
    assert schema.min_30_day == Decimal("1500.00")
    assert schema.min_60_day == Decimal("3000.00")
    assert schema.min_90_day == Decimal("5000.00")
    assert schema.daily_deficit == Decimal("35.00")
    assert schema.yearly_deficit == Decimal("12775.00")
    assert schema.required_income == Decimal("15000.00")
    assert schema.hourly_rate_40 == Decimal("25.00")
    assert schema.hourly_rate_30 == Decimal("33.33")
    assert schema.hourly_rate_20 == Decimal("50.00")

    # Verify forecast_date using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.forecast_date, now)


def test_create_cashflow_update_schema_empty():
    """Test creating an empty CashflowUpdate schema."""
    schema = create_cashflow_update_schema()

    assert isinstance(schema, CashflowUpdate)
    assert schema.total_bills is None
    assert schema.total_income is None
    assert schema.balance is None
    assert schema.forecast is None
    assert schema.min_14_day is None
    assert schema.min_30_day is None
    assert schema.min_60_day is None
    assert schema.min_90_day is None
    assert schema.daily_deficit is None
    assert schema.yearly_deficit is None
    assert schema.required_income is None
    assert schema.hourly_rate_40 is None
    assert schema.hourly_rate_30 is None
    assert schema.hourly_rate_20 is None
    assert schema.forecast_date is None


def test_create_cashflow_update_schema_with_all_values():
    """Test creating a CashflowUpdate schema with all fields."""
    now = utc_now()

    schema = create_cashflow_update_schema(
        total_bills=Decimal("200.00"),
        total_income=Decimal("3000.00"),
        balance=Decimal("2500.00"),
        forecast=Decimal("5000.00"),
        min_14_day=Decimal("800.00"),
        min_30_day=Decimal("1500.00"),
        min_60_day=Decimal("3000.00"),
        min_90_day=Decimal("5000.00"),
        daily_deficit=Decimal("35.00"),
        yearly_deficit=Decimal("12775.00"),
        required_income=Decimal("15000.00"),
        hourly_rate_40=Decimal("25.00"),
        hourly_rate_30=Decimal("33.33"),
        hourly_rate_20=Decimal("50.00"),
        forecast_date=now,
    )

    assert isinstance(schema, CashflowUpdate)
    assert schema.total_bills == Decimal("200.00")
    assert schema.total_income == Decimal("3000.00")
    assert schema.balance == Decimal("2500.00")
    assert schema.forecast == Decimal("5000.00")
    assert schema.min_14_day == Decimal("800.00")
    assert schema.min_30_day == Decimal("1500.00")
    assert schema.min_60_day == Decimal("3000.00")
    assert schema.min_90_day == Decimal("5000.00")
    assert schema.daily_deficit == Decimal("35.00")
    assert schema.yearly_deficit == Decimal("12775.00")
    assert schema.required_income == Decimal("15000.00")
    assert schema.hourly_rate_40 == Decimal("25.00")
    assert schema.hourly_rate_30 == Decimal("33.33")
    assert schema.hourly_rate_20 == Decimal("50.00")

    # Verify forecast_date using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.forecast_date, now)


def test_create_cashflow_update_schema_with_partial_values():
    """Test creating a CashflowUpdate schema with partial fields."""
    now = utc_now()

    schema = create_cashflow_update_schema(
        total_bills=Decimal("200.00"),
        balance=Decimal("2500.00"),
        min_14_day=Decimal("800.00"),
        daily_deficit=Decimal("35.00"),
        forecast_date=now,
    )

    assert isinstance(schema, CashflowUpdate)
    assert schema.total_bills == Decimal("200.00")
    assert schema.total_income is None
    assert schema.balance == Decimal("2500.00")
    assert schema.forecast is None
    assert schema.min_14_day == Decimal("800.00")
    assert schema.min_30_day is None
    assert schema.min_60_day is None
    assert schema.min_90_day is None
    assert schema.daily_deficit == Decimal("35.00")
    assert schema.yearly_deficit is None
    assert schema.required_income is None
    assert schema.hourly_rate_40 is None
    assert schema.hourly_rate_30 is None
    assert schema.hourly_rate_20 is None

    # Verify forecast_date using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.forecast_date, now)


def test_create_cashflow_filters_schema_empty():
    """Test creating an empty CashflowFilters schema."""
    schema = create_cashflow_filters_schema()

    assert isinstance(schema, CashflowFilters)
    assert schema.start_date is None
    assert schema.end_date is None
    assert schema.min_balance is None
    assert schema.max_balance is None


def test_create_cashflow_filters_schema_with_all_fields():
    """Test creating a CashflowFilters schema with all fields."""
    start_date = utc_now()
    end_date = utc_now()

    schema = create_cashflow_filters_schema(
        start_date=start_date,
        end_date=end_date,
        min_balance=Decimal("1000.00"),
        max_balance=Decimal("5000.00"),
    )

    assert isinstance(schema, CashflowFilters)

    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)
    assert datetime_equals(schema.end_date, end_date)

    assert schema.min_balance == Decimal("1000.00")
    assert schema.max_balance == Decimal("5000.00")


def test_create_cashflow_filters_schema_with_partial_fields():
    """Test creating a CashflowFilters schema with partial fields."""
    start_date = utc_now()

    schema = create_cashflow_filters_schema(
        start_date=start_date, min_balance=Decimal("1000.00")
    )

    assert isinstance(schema, CashflowFilters)

    # Verify datetime field using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)

    assert schema.end_date is None
    assert schema.min_balance == Decimal("1000.00")
    assert schema.max_balance is None
