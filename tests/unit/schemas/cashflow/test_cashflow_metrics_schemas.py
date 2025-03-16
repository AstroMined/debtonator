from decimal import Decimal
import pytest
from pydantic import ValidationError

from src.schemas.cashflow.metrics import (
    MinimumRequired,
    DeficitCalculation,
    HourlyRates
)


def test_minimum_required_valid():
    """Test valid minimum required schema creation"""
    min_required = MinimumRequired(
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00")
    )

    assert min_required.min_14_day == Decimal("500.00")
    assert min_required.min_30_day == Decimal("1000.00")
    assert min_required.min_60_day == Decimal("2000.00")
    assert min_required.min_90_day == Decimal("3000.00")


def test_deficit_calculation_valid():
    """Test valid deficit calculation schema creation"""
    deficit = DeficitCalculation(
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00")
    )

    assert deficit.daily_deficit == Decimal("50.00")
    assert deficit.yearly_deficit == Decimal("18250.00")
    assert deficit.required_income == Decimal("2000.00")


def test_hourly_rates_valid():
    """Test valid hourly rates schema creation"""
    rates = HourlyRates(
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )

    assert rates.hourly_rate_40 == Decimal("12.50")
    assert rates.hourly_rate_30 == Decimal("16.67")
    assert rates.hourly_rate_20 == Decimal("25.00")


# Test field validations

def test_minimum_required_field_required():
    """Test required fields validation in minimum required schema"""
    # Test missing min_14_day
    with pytest.raises(ValidationError, match="Field required"):
        MinimumRequired(
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00")
        )

    # Test missing min_30_day
    with pytest.raises(ValidationError, match="Field required"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00")
        )

    # Test missing min_60_day
    with pytest.raises(ValidationError, match="Field required"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_90_day=Decimal("3000.00")
        )

    # Test missing min_90_day
    with pytest.raises(ValidationError, match="Field required"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00")
        )


def test_deficit_calculation_field_required():
    """Test required fields validation in deficit calculation schema"""
    # Test missing daily_deficit
    with pytest.raises(ValidationError, match="Field required"):
        DeficitCalculation(
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00")
        )

    # Test missing yearly_deficit
    with pytest.raises(ValidationError, match="Field required"):
        DeficitCalculation(
            daily_deficit=Decimal("50.00"),
            required_income=Decimal("2000.00")
        )

    # Test missing required_income
    with pytest.raises(ValidationError, match="Field required"):
        DeficitCalculation(
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00")
        )


def test_hourly_rates_field_required():
    """Test required fields validation in hourly rates schema"""
    # Test missing hourly_rate_40
    with pytest.raises(ValidationError, match="Field required"):
        HourlyRates(
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )

    # Test missing hourly_rate_30
    with pytest.raises(ValidationError, match="Field required"):
        HourlyRates(
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_20=Decimal("25.00")
        )

    # Test missing hourly_rate_20
    with pytest.raises(ValidationError, match="Field required"):
        HourlyRates(
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67")
        )


def test_minimum_required_decimal_precision():
    """Test decimal precision validation in minimum required schema"""
    # Test too many decimal places in min_14_day
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        MinimumRequired(
            min_14_day=Decimal("500.123"),  # Too many decimal places
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00")
        )

    # Test too many decimal places in min_30_day
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.123"),  # Too many decimal places
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.00")
        )

    # Test too many decimal places in min_60_day
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.123"),  # Too many decimal places
            min_90_day=Decimal("3000.00")
        )

    # Test too many decimal places in min_90_day
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        MinimumRequired(
            min_14_day=Decimal("500.00"),
            min_30_day=Decimal("1000.00"),
            min_60_day=Decimal("2000.00"),
            min_90_day=Decimal("3000.123")  # Too many decimal places
        )


def test_deficit_calculation_decimal_precision():
    """Test decimal precision validation in deficit calculation schema"""
    # Test too many decimal places in daily_deficit
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        DeficitCalculation(
            daily_deficit=Decimal("50.123"),  # Too many decimal places
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.00")
        )

    # Test too many decimal places in yearly_deficit
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        DeficitCalculation(
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.123"),  # Too many decimal places
            required_income=Decimal("2000.00")
        )

    # Test too many decimal places in required_income
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        DeficitCalculation(
            daily_deficit=Decimal("50.00"),
            yearly_deficit=Decimal("18250.00"),
            required_income=Decimal("2000.123")  # Too many decimal places
        )


def test_hourly_rates_decimal_precision():
    """Test decimal precision validation in hourly rates schema"""
    # Test too many decimal places in hourly_rate_40
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        HourlyRates(
            hourly_rate_40=Decimal("12.501"),  # Too many decimal places
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.00")
        )

    # Test too many decimal places in hourly_rate_30
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        HourlyRates(
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.671"),  # Too many decimal places
            hourly_rate_20=Decimal("25.00")
        )

    # Test too many decimal places in hourly_rate_20
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        HourlyRates(
            hourly_rate_40=Decimal("12.50"),
            hourly_rate_30=Decimal("16.67"),
            hourly_rate_20=Decimal("25.001")  # Too many decimal places
        )


def test_base_schema_validator_inheritance():
    """Test BaseSchemaValidator inheritance"""
    # Create valid instances of each schema
    min_required = MinimumRequired(
        min_14_day=Decimal("500.00"),
        min_30_day=Decimal("1000.00"),
        min_60_day=Decimal("2000.00"),
        min_90_day=Decimal("3000.00")
    )
    
    deficit = DeficitCalculation(
        daily_deficit=Decimal("50.00"),
        yearly_deficit=Decimal("18250.00"),
        required_income=Decimal("2000.00")
    )
    
    rates = HourlyRates(
        hourly_rate_40=Decimal("12.50"),
        hourly_rate_30=Decimal("16.67"),
        hourly_rate_20=Decimal("25.00")
    )
    
    # Verify all can be converted to dictionary format
    min_required_dict = min_required.model_dump()
    deficit_dict = deficit.model_dump()
    rates_dict = rates.model_dump()
    
    assert isinstance(min_required_dict, dict)
    assert isinstance(deficit_dict, dict)
    assert isinstance(rates_dict, dict)
    
    # Check the dictionaries contain the expected keys
    assert "min_14_day" in min_required_dict
    assert "min_30_day" in min_required_dict
    assert "min_60_day" in min_required_dict
    assert "min_90_day" in min_required_dict
    
    assert "daily_deficit" in deficit_dict
    assert "yearly_deficit" in deficit_dict
    assert "required_income" in deficit_dict
    
    assert "hourly_rate_40" in rates_dict
    assert "hourly_rate_30" in rates_dict
    assert "hourly_rate_20" in rates_dict
