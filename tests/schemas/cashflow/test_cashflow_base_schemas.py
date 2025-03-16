from datetime import datetime, timezone, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.cashflow.base import (
    CashflowBase,
    CashflowCreate,
    CashflowUpdate,
    CashflowInDB,
    CashflowResponse,
    CashflowList,
    CashflowFilters
)


def test_cashflow_base_valid():
    """Test valid cashflow base schema creation"""
    now = datetime.now(timezone.utc)
    cashflow = CashflowBase(
        forecast_date=now,
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )

    assert cashflow.forecast_date == now
    assert cashflow.total_bills == Decimal("1500.00")
    assert cashflow.total_income == Decimal("2500.00")
    assert cashflow.balance == Decimal("1000.00")
    assert cashflow.forecast == Decimal("2000.00")
    assert cashflow.min_14_day == Decimal("500.00")
    assert cashflow.min_30_day == Decimal("1000.00")
    assert cashflow.min_60_day == Decimal("2000.00")
    assert cashflow.min_90_day == Decimal("3000.00")
    assert cashflow.daily_deficit == Decimal("50.00")
    assert cashflow.yearly_deficit == Decimal("18250.00")
    assert cashflow.required_income == Decimal("2000.00")
    assert cashflow.hourly_rate_40 == Decimal("12.50")
    assert cashflow.hourly_rate_30 == Decimal("16.67")
    assert cashflow.hourly_rate_20 == Decimal("25.00")


def test_cashflow_base_default_timestamp():
    """Test default forecast_date in UTC timezone"""
    before = datetime.now(timezone.utc)
    
    # Create instance with default forecast_date
    cashflow = CashflowBase(
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )
    
    after = datetime.now(timezone.utc)
    
    # After our fix, default datetime values should be properly timezone aware
    # The model_validator we added ensures this behavior
    
    # Verify the default timestamp has a UTC timezone
    assert cashflow.forecast_date.tzinfo is not None, "Default timestamp should have timezone info"
    assert cashflow.forecast_date.utcoffset().total_seconds() == 0, "Default timestamp should be in UTC timezone"
    
    # Verify the timestamp is within the expected range
    assert before <= cashflow.forecast_date <= after, "Default timestamp should be between before and after"


def test_cashflow_create_valid():
    """Test valid cashflow create schema"""
    now = datetime.now(timezone.utc)
    cashflow = CashflowCreate(
        forecast_date=now,
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )

    assert cashflow.forecast_date == now
    assert cashflow.total_bills == Decimal("1500.00")
    assert cashflow.total_income == Decimal("2500.00")


def test_cashflow_update_valid():
    """Test valid cashflow update schema"""
    now = datetime.now(timezone.utc)
    
    # Empty update (all fields optional)
    empty_update = CashflowUpdate()
    assert empty_update.forecast_date is None
    assert empty_update.total_bills is None
    
    # Partial update
    partial_update = CashflowUpdate(
        forecast_date=now,
        total_bills=Decimal("1800.00"),
        min_30_day=Decimal("1200.00")
    )
    
    assert partial_update.forecast_date == now
    assert partial_update.total_bills == Decimal("1800.00")
    assert partial_update.min_30_day == Decimal("1200.00")
    assert partial_update.total_income is None


def test_cashflow_in_db_valid():
    """Test valid cashflow in DB schema"""
    now = datetime.now(timezone.utc)
    cashflow = CashflowInDB(
        id=1,
        created_at=now,
        updated_at=now,
        forecast_date=now,
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )

    assert cashflow.id == 1
    assert cashflow.created_at == now
    assert cashflow.updated_at == now
    assert cashflow.forecast_date == now


def test_cashflow_response_valid():
    """Test valid cashflow response schema"""
    now = datetime.now(timezone.utc)
    response = CashflowResponse(
        id=1,
        created_at=now,
        updated_at=now,
        forecast_date=now,
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )

    assert response.id == 1
    assert response.created_at == now
    assert response.updated_at == now


def test_cashflow_list_valid():
    """Test valid cashflow list schema"""
    now = datetime.now(timezone.utc)
    cashflow1 = CashflowResponse(
        id=1,
        created_at=now,
        updated_at=now,
        forecast_date=now,
        total_bills=Decimal("1500.00"),
        total_income=Decimal("2500.00"),
        balance=Decimal("1000.00"),
        forecast=Decimal("2000.00"),
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00"),
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00"),
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )
    
    cashflow2 = CashflowResponse(
        id=2,
        created_at=now,
        updated_at=now,
        forecast_date=now,
        total_bills=Decimal("1600.00"),
        total_income=Decimal("2600.00"),
        balance=Decimal("1100.00"),
        forecast=Decimal("2100.00"),
        min_14_day=Decimal("600.00"),
        min_30_day=Decimal("1100.00"),
        min_60_day=Decimal("2100.00"),
        min_90_day=Decimal("3100.00"),
        daily_deficit=Decimal("51.00"),
        yearly_deficit=Decimal("18615.00"),
        required_income=Decimal("2100.00"),
        hourly_rate_40=Decimal("13.13"),
        hourly_rate_30=Decimal("17.50"),
        hourly_rate_20=Decimal("26.25")
    )
    
    cashflow_list = CashflowList(
        items=[cashflow1, cashflow2],
        total=2
    )
    
    assert len(cashflow_list.items) == 2
    assert cashflow_list.total == 2
    assert cashflow_list.items[0].id == 1
    assert cashflow_list.items[1].id == 2


def test_cashflow_filters_valid():
    """Test valid cashflow filters schema"""
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=30)
    
    filters = CashflowFilters(
        start_date=start_date,
        end_date=end_date,
        min_balance=Decimal("500.00"),
        max_balance=Decimal("5000.00")
    )
    
    assert filters.start_date == start_date
    assert filters.end_date == end_date
    assert filters.min_balance == Decimal("500.00")
    assert filters.max_balance == Decimal("5000.00")
    
    # Test with some fields missing (all are optional)
    partial_filters = CashflowFilters(
        start_date=start_date,
        min_balance=Decimal("500.00")
    )
    
    assert partial_filters.start_date == start_date
    assert partial_filters.end_date is None
    assert partial_filters.min_balance == Decimal("500.00")
    assert partial_filters.max_balance is None


# Test field validations
def test_required_fields():
    """Test required fields validation"""
    # Test missing required fields
    with pytest.raises(ValidationError, match="Field required"):
        CashflowBase(
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )

    with pytest.raises(ValidationError, match="Field required"):
        CashflowBase(
            total_bills=Decimal("1500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places in various fields
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        CashflowBase(
            total_bills=Decimal("1500.123"),  # Too many decimal places
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )

    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        CashflowBase(
            total_bills=Decimal("1500.00"),
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.123"),  # Too many decimal places
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )


def test_negative_amounts():
    """Test validation of negative amounts where not allowed"""
    # Test negative total_bills
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        CashflowBase(
            total_bills=Decimal("-1500.00"),  # Negative value
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )

    # Test negative total_income
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        CashflowBase(
            total_bills=Decimal("1500.00"),
            total_income=Decimal("-2500.00"),  # Negative value
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now = datetime.now(timezone.utc)
    
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowBase(
            forecast_date=datetime.now(),  # Naive datetime
            total_bills=Decimal("1500.00"),
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )
    
    # Test non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowBase(
            forecast_date=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
            total_bills=Decimal("1500.00"),
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )
    
    # Test filter with naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowFilters(
            start_date=datetime.now(),  # Naive datetime
            end_date=now
        )
    
    # Test filter with non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowFilters(
            start_date=now,
            end_date=datetime.now(ZoneInfo("America/New_York"))  # Non-UTC timezone
        )


def test_in_db_timestamps():
    """Test UTC validation for database timestamps"""
    now = datetime.now(timezone.utc)
    
    # Test naive created_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowInDB(
            id=1,
            created_at=datetime.now(),  # Naive datetime
            updated_at=now,
            forecast_date=now,
            total_bills=Decimal("1500.00"),
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )
    
    # Test non-UTC updated_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CashflowInDB(
            id=1,
            created_at=now,
            updated_at=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
            forecast_date=now,
            total_bills=Decimal("1500.00"),
            total_income=Decimal("2500.00"),
            balance=Decimal("1000.00"),
            forecast=Decimal("2000.00"),
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00"),
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00"),
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )
