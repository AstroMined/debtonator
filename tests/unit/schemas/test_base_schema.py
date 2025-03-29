"""
Tests for the BaseSchemaValidator class and common schema validations.

These tests ensure the base validation functionality works correctly and follows 
ADR-011 requirements for datetime standardization.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Union
from zoneinfo import ZoneInfo
import importlib
import sys

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.schemas.base_schema import (
    BaseSchemaValidator,
    CorrelationDecimal,
    CorrelationDict,
    IntMoneyDict,
    IntPercentageDict,
    MoneyDecimal,
    MoneyDict,
    PercentageDecimal,
    PercentageDict,
    RatioDecimal,
    RatioDict,
)
from src.utils.datetime_utils import (
    days_ago,
    days_from_now,
    ensure_utc,
    is_adr011_compliant,
    utc_datetime,
    utc_now,
)


# Test model classes to exercise BaseSchemaValidator functionality
class SimpleModel(BaseSchemaValidator):
    """Simple model to test basic validation."""
    name: str
    created_at: datetime


class MoneyModel(BaseSchemaValidator):
    """Model to test money decimal validation."""
    amount: MoneyDecimal
    optional_amount: Optional[MoneyDecimal] = None


class PercentageModel(BaseSchemaValidator):
    """Model to test percentage decimal validation."""
    value: PercentageDecimal
    optional_value: Optional[PercentageDecimal] = None


class CorrelationModel(BaseSchemaValidator):
    """Model to test correlation decimal validation."""
    correlation: CorrelationDecimal
    optional_correlation: Optional[CorrelationDecimal] = None


class RatioModel(BaseSchemaValidator):
    """Model to test ratio decimal validation."""
    ratio: RatioDecimal
    optional_ratio: Optional[RatioDecimal] = None


class DictionaryModel(BaseSchemaValidator):
    """Model to test dictionary validations."""
    money_dict: MoneyDict = {}
    percentage_dict: PercentageDict = {}
    correlation_dict: CorrelationDict = {}
    ratio_dict: RatioDict = {}
    int_money_dict: IntMoneyDict = {}
    int_percentage_dict: IntPercentageDict = {}


class NonAnnotatedDictModel(BaseSchemaValidator):
    """Model with a dictionary field that has no type annotation."""
    # This field has no type annotation for dict values
    generic_dict: Dict = {}


class DefaultDatetimeModel(BaseSchemaValidator):
    """Model to test default datetime values."""
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=utc_now)


class UpdateModel(BaseSchemaValidator):
    """Model to test update validation."""
    name: Optional[str] = None
    value: Optional[MoneyDecimal] = None

    model_config = ConfigDict(
        extra="ignore",
    )

    # Flag to identify this as an update schema for test purposes
    __test_update_schema__ = True


class ModelWithNonNullableField(BaseModel):
    """Mock SQLAlchemy model with non-nullable field for testing."""
    __tablename__ = "test_model"
    
    class __table__:
        class columns:
            name = type("Column", (), {"nullable": False})
            value = type("Column", (), {"nullable": True})


class UpdateModelWithModelRef(BaseSchemaValidator):
    """Update model with a model class reference for testing nullable validation."""
    name: Optional[str] = None
    value: Optional[MoneyDecimal] = None
    
    # Reference to model class for validation
    __model__ = ModelWithNonNullableField


class AccountUpdate(BaseSchemaValidator):
    """Update model that has a name matching a pattern in src.models."""
    name: Optional[str] = None
    value: Optional[MoneyDecimal] = None


def test_base_schema_validator_utc_datetime_validation():
    """Test that datetime fields are validated for UTC timezone."""
    # Valid UTC datetime
    now_utc = utc_now()
    model = SimpleModel(name="Test", created_at=now_utc)
    assert model.created_at == now_utc
    assert is_adr011_compliant(model.created_at)
    
    # Invalid naive datetime
    naive_dt = datetime.now()
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        SimpleModel(name="Test", created_at=naive_dt)
    
    # Invalid non-UTC timezone
    eastern = ZoneInfo("America/New_York")
    non_utc_dt = datetime.now(eastern)
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        SimpleModel(name="Test", created_at=non_utc_dt)


def test_model_validate_method():
    """Test the model_validate method converts naive datetimes to UTC."""
    # Create a mock object that would come from SQLAlchemy
    class MockObject:
        def __init__(self):
            self.name = "Test"
            # SQLAlchemy returns naive datetimes
            self.created_at = datetime.utcnow()
    
    mock_obj = MockObject()
    
    # Validate should convert the naive datetime to UTC
    model = SimpleModel.model_validate(mock_obj)
    assert model.name == "Test"
    assert model.created_at.tzinfo is not None
    assert model.created_at.tzinfo == timezone.utc
    
    # Test with dictionary input that has timezone-aware datetime using utc_now
    dt = utc_now()
    dict_input = {"name": "Test", "created_at": dt}
    model = SimpleModel.model_validate(dict_input)
    assert is_adr011_compliant(model.created_at)


def test_model_validate_fallback_path():
    """Test the fallback path in model_validate method."""
    # Test objects without __dict__ attribute (lines 122-135)
    class NonDictObject:
        # This object doesn't use __dict__ for attribute storage
        __slots__ = ["name", "created_at"]
        
        def __init__(self):
            self.name = "Test"
            self.created_at = utc_now()
    
    non_dict_obj = NonDictObject()
    
    # This should fall back to the standard validation path
    model = SimpleModel.model_validate(non_dict_obj, from_attributes=True)
    assert model.name == "Test"
    assert model.created_at.tzinfo == timezone.utc
    
    # Test with a dictionary but from_attributes=False (should use standard path)
    dict_input = {"name": "Test", "created_at": utc_now()}
    model = SimpleModel.model_validate(dict_input, from_attributes=False)
    assert model.name == "Test"
    assert model.created_at.tzinfo == timezone.utc


def test_default_datetime_handling():
    """Test handling of default_factory datetime values."""
    # Default factory values should be validated and made timezone-aware
    model = DefaultDatetimeModel(name="Test")
    
    # created_at uses datetime.now (naive) but should be converted to UTC
    assert model.created_at.tzinfo is not None
    assert model.created_at.tzinfo == timezone.utc
    
    # updated_at uses utc_now (already UTC) and should remain UTC
    assert model.updated_at.tzinfo is not None
    assert model.updated_at.tzinfo == timezone.utc


def test_money_decimal_validation():
    """Test MoneyDecimal validation rules."""
    # Valid values
    valid_model = MoneyModel(amount=Decimal("100.00"))
    assert valid_model.amount == Decimal("100.00")
    
    # Test various decimal formats
    assert MoneyModel(amount=Decimal("100")).amount == Decimal("100")
    assert MoneyModel(amount=Decimal("100.5")).amount == Decimal("100.5")
    assert MoneyModel(amount=Decimal("100.50")).amount == Decimal("100.50")
    
    # Too many decimal places
    with pytest.raises(ValidationError, match="multiple_of"):
        MoneyModel(amount=Decimal("100.001"))
    
    # Optional field
    valid_model = MoneyModel(amount=Decimal("100.00"), optional_amount=None)
    assert valid_model.optional_amount is None


def test_percentage_decimal_validation():
    """Test PercentageDecimal validation rules."""
    # Valid values
    valid_model = PercentageModel(value=Decimal("0.5000"))
    assert valid_model.value == Decimal("0.5000")
    
    # Zero is valid
    assert PercentageModel(value=Decimal("0")).value == Decimal("0")
    
    # One is valid (100%)
    assert PercentageModel(value=Decimal("1")).value == Decimal("1")
    
    # Test various decimal formats within range
    assert PercentageModel(value=Decimal("0.5")).value == Decimal("0.5")
    assert PercentageModel(value=Decimal("0.75")).value == Decimal("0.75")
    assert PercentageModel(value=Decimal("0.123")).value == Decimal("0.123")
    
    # Too many decimal places
    with pytest.raises(ValidationError, match="multiple_of"):
        PercentageModel(value=Decimal("0.12345"))
    
    # Less than 0
    with pytest.raises(ValidationError, match="greater than or equal to"):
        PercentageModel(value=Decimal("-0.1"))
    
    # Greater than 1
    with pytest.raises(ValidationError, match="less than or equal to"):
        PercentageModel(value=Decimal("1.1"))
    
    # Optional field
    valid_model = PercentageModel(value=Decimal("0.5000"), optional_value=None)
    assert valid_model.optional_value is None


def test_correlation_decimal_validation():
    """Test CorrelationDecimal validation rules."""
    # Valid values
    valid_model = CorrelationModel(correlation=Decimal("0.8500"))
    assert valid_model.correlation == Decimal("0.8500")
    
    # Negative values are valid
    assert CorrelationModel(correlation=Decimal("-0.5")).correlation == Decimal("-0.5")
    
    # Boundary values are valid
    assert CorrelationModel(correlation=Decimal("-1")).correlation == Decimal("-1")
    assert CorrelationModel(correlation=Decimal("1")).correlation == Decimal("1")
    
    # Too many decimal places
    with pytest.raises(ValidationError, match="multiple_of"):
        CorrelationModel(correlation=Decimal("0.12345"))
    
    # Less than -1
    with pytest.raises(ValidationError, match="greater than or equal to"):
        CorrelationModel(correlation=Decimal("-1.1"))
    
    # Greater than 1
    with pytest.raises(ValidationError, match="less than or equal to"):
        CorrelationModel(correlation=Decimal("1.1"))
    
    # Optional field
    valid_model = CorrelationModel(correlation=Decimal("0.5000"), optional_correlation=None)
    assert valid_model.optional_correlation is None


def test_ratio_decimal_validation():
    """Test RatioDecimal validation rules."""
    # Valid values
    valid_model = RatioModel(ratio=Decimal("2.5000"))
    assert valid_model.ratio == Decimal("2.5000")
    
    # Negative values are valid (unlike Percentage)
    assert RatioModel(ratio=Decimal("-1.5")).ratio == Decimal("-1.5")
    
    # Zero is valid
    assert RatioModel(ratio=Decimal("0")).ratio == Decimal("0")
    
    # Large values are valid
    assert RatioModel(ratio=Decimal("1000")).ratio == Decimal("1000")
    
    # Too many decimal places
    with pytest.raises(ValidationError, match="multiple_of"):
        RatioModel(ratio=Decimal("2.12345"))
    
    # Optional field
    valid_model = RatioModel(ratio=Decimal("2.5000"), optional_ratio=None)
    assert valid_model.optional_ratio is None


def test_dictionary_model_validation():
    """Test dictionary field validations."""
    # Valid empty dictionaries
    model = DictionaryModel()
    assert model.money_dict == {}
    assert model.percentage_dict == {}
    assert model.correlation_dict == {}
    assert model.ratio_dict == {}
    assert model.int_money_dict == {}
    assert model.int_percentage_dict == {}
    
    # Valid MoneyDict
    valid_money_dict = {"item1": Decimal("10.50"), "item2": Decimal("20.00")}
    model = DictionaryModel(money_dict=valid_money_dict)
    assert model.money_dict == valid_money_dict
    
    # Invalid MoneyDict (too many decimal places)
    invalid_money_dict = {"item1": Decimal("10.501")}
    with pytest.raises(ValidationError, match="should have no more than 2 decimal places"):
        DictionaryModel(money_dict=invalid_money_dict)
    
    # Valid PercentageDict
    valid_percentage_dict = {"item1": Decimal("0.5000"), "item2": Decimal("0.7500")}
    model = DictionaryModel(percentage_dict=valid_percentage_dict)
    assert model.percentage_dict == valid_percentage_dict
    
    # Invalid PercentageDict (out of range)
    invalid_percentage_dict = {"item1": Decimal("1.5")}
    with pytest.raises(ValidationError, match="must be between 0 and 1"):
        DictionaryModel(percentage_dict=invalid_percentage_dict)
    
    # Invalid PercentageDict (too many decimal places)
    invalid_percentage_dict = {"item1": Decimal("0.12345")}
    with pytest.raises(ValidationError, match="should have no more than 4 decimal places"):
        DictionaryModel(percentage_dict=invalid_percentage_dict)
    
    # Valid CorrelationDict
    valid_correlation_dict = {"item1": Decimal("0.8000"), "item2": Decimal("-0.5000")}
    model = DictionaryModel(correlation_dict=valid_correlation_dict)
    assert model.correlation_dict == valid_correlation_dict
    
    # Invalid CorrelationDict (out of range)
    invalid_correlation_dict = {"item1": Decimal("1.5")}
    with pytest.raises(ValidationError, match="must be between -1 and 1"):
        DictionaryModel(correlation_dict=invalid_correlation_dict)
    
    # Valid RatioDict
    valid_ratio_dict = {"item1": Decimal("2.5000"), "item2": Decimal("-1.5000")}
    model = DictionaryModel(ratio_dict=valid_ratio_dict)
    assert model.ratio_dict == valid_ratio_dict
    
    # Invalid RatioDict (too many decimal places)
    invalid_ratio_dict = {"item1": Decimal("2.12345")}
    with pytest.raises(ValidationError, match="should have no more than 4 decimal places"):
        DictionaryModel(ratio_dict=invalid_ratio_dict)
    
    # Valid IntMoneyDict
    valid_int_money_dict = {1: Decimal("10.50"), 2: Decimal("20.00")}
    model = DictionaryModel(int_money_dict=valid_int_money_dict)
    assert model.int_money_dict == valid_int_money_dict
    
    # Invalid IntMoneyDict (too many decimal places)
    invalid_int_money_dict = {1: Decimal("10.501")}
    with pytest.raises(ValidationError, match="should have no more than 2 decimal places"):
        DictionaryModel(int_money_dict=invalid_int_money_dict)


def test_non_dict_field_validation():
    """Test that non-dictionary fields are skipped in dictionary validation."""
    # This model has a field that isn't a dictionary
    class MixedModel(BaseSchemaValidator):
        non_dict_field: str = "test"
        money_dict: MoneyDict = {"item": Decimal("10.50")}
    
    # This should not raise any errors (non-dict fields are skipped)
    model = MixedModel()
    assert model.non_dict_field == "test"
    assert model.money_dict == {"item": Decimal("10.50")}


def test_dict_field_without_annotation():
    """Test dictionary field without type annotation is skipped."""
    # Create a model with a generic Dict field (no value type annotation)
    model = NonAnnotatedDictModel(generic_dict={"key": "value"})
    
    # This shouldn't raise any validation errors
    assert model.generic_dict == {"key": "value"}
    
    # Even with a decimal value that would normally be invalid
    model = NonAnnotatedDictModel(generic_dict={"key": Decimal("123.45678")})
    assert model.generic_dict["key"] == Decimal("123.45678")


def test_dict_field_with_non_decimal_values():
    """Test dictionary field with non-decimal values is handled correctly."""
    # Create a model with a MoneyDict but try to use non-Decimal values
    class TestModel(BaseSchemaValidator):
        money_dict: MoneyDict = {}
    
    # String values should be accepted during initial validation
    # (Pydantic will convert compatible strings to Decimal)
    model = TestModel(money_dict={"item": "10.50"})
    assert isinstance(model.money_dict["item"], Decimal)
    assert model.money_dict["item"] == Decimal("10.50")
    
    # But non-convertible values should fail
    with pytest.raises(ValidationError):
        TestModel(money_dict={"item": "not-a-number"})


def test_update_model_validation():
    """Test validation for update models with optional fields."""
    # Empty update is valid
    update = UpdateModel()
    assert update.name is None
    assert update.value is None
    
    # Partial update is valid
    update = UpdateModel(name="Updated")
    assert update.name == "Updated"
    assert update.value is None
    
    # Full update is valid
    update = UpdateModel(name="Updated", value=Decimal("100.00"))
    assert update.name == "Updated"
    assert update.value == Decimal("100.00")
    
    # Invalid money value
    with pytest.raises(ValidationError, match="multiple_of"):
        UpdateModel(value=Decimal("100.001"))


def test_required_fields_validation_for_update_schema():
    """Test validation of required fields not being None in update schemas."""
    # For regular models, setting required fields to None shouldn't trigger the validator
    model = UpdateModel(name=None)
    assert model.name is None
    
    # For update models with model references, nullability should be checked
    with pytest.raises(ValidationError, match="cannot be set to None"):
        UpdateModelWithModelRef(name=None, value=Decimal("100.00"))
    
    # But nullable fields can be set to None
    model = UpdateModelWithModelRef(name="Test", value=None)
    assert model.name == "Test"
    assert model.value is None


def test_required_fields_dynamic_model_lookup():
    """Test dynamic model lookup for required fields validation.
    
    Tests lines 294->307, 303-304, 308-310 in base_schema.py.
    """
    # Create a mock Account model with a non-nullable name field
    class MockAccount:
        __table__ = type("Table", (), {
            "columns": type("Columns", (), {
                "name": type("Column", (), {"nullable": False}),
                "value": type("Column", (), {"nullable": True})
            })
        })
    
    # Save original import_module function
    original_import = importlib.import_module
    
    # Create a mock import function
    def mock_import_module(name, package=None):
        if name == "src.models":
            # Return a mock module with Account class
            return type("Module", (), {"Account": MockAccount})
        return original_import(name, package)
    
    # Patch the import_module function
    importlib.import_module = mock_import_module
    
    try:
        # This should fail because 'name' is non-nullable in the mocked Account model
        with pytest.raises(ValueError, match="cannot be set to None"):
            AccountUpdate(name=None)
        
        # Check that nullable fields can be set to None
        model = AccountUpdate(name="Test", value=None)
        assert model.name == "Test"
        assert model.value is None
    finally:
        # Restore the original import function
        importlib.import_module = original_import


def test_json_encoder_config():
    """Test JSON encoder configuration correctly formats datetimes."""
    # Create model with a datetime
    now = utc_now()
    model = SimpleModel(name="Test", created_at=now)
    
    # Convert to dict
    model_dict = model.model_dump(mode="json")
    
    # Check datetime format contains Z suffix for UTC time
    assert "Z" in model_dict["created_at"]
    assert "+00:00" not in model_dict["created_at"]


def test_ensure_datetime_fields_are_utc():
    """Test ensure_datetime_fields_are_utc validator converts naive datetimes."""
    # Create a class that sets a naive datetime after initialization
    class PostInitModel(BaseSchemaValidator):
        name: str
        created_at: datetime
        
        @field_validator("created_at", mode="after")
        @classmethod
        def set_naive_datetime(cls, v):
            # This would bypass the main validator, but ensure_datetime_fields_are_utc should catch it
            return datetime.now()
    
    # Initialize with a valid UTC datetime
    model = PostInitModel(name="Test", created_at=utc_now())
    
    # The validator should convert the naive datetime set by set_naive_datetime to UTC
    assert model.created_at.tzinfo is not None
    assert model.created_at.tzinfo == timezone.utc


def test_datetimes_with_varying_tzinfo_implementations():
    """Test that different tzinfo implementations are handled correctly."""
    # Create a datetime with timezone.utc
    dt1 = datetime.now(timezone.utc)
    
    # Create a datetime with a timedelta timezone (also UTC)
    dt2 = datetime.now(timezone(timedelta(hours=0)))
    
    # Both should validate
    model1 = SimpleModel(name="Test1", created_at=dt1)
    model2 = SimpleModel(name="Test2", created_at=dt2)
    
    assert model1.created_at.tzinfo == timezone.utc
    # The second datetime may keep its original tzinfo implementation
    # but should be semantically equivalent to UTC
    assert model2.created_at.utcoffset().total_seconds() == 0


def test_integration_with_datetime_utils():
    """Test integration with datetime_utils functions."""
    # Test with utc_now
    model = SimpleModel(name="Test", created_at=utc_now())
    assert is_adr011_compliant(model.created_at)
    
    # Test with utc_datetime
    specific_dt = utc_datetime(2025, 3, 15, 14, 30)
    model = SimpleModel(name="Test", created_at=specific_dt)
    assert is_adr011_compliant(model.created_at)
    assert model.created_at.year == 2025
    assert model.created_at.month == 3
    assert model.created_at.day == 15
    
    # Test with days_ago
    past_dt = days_ago(7)
    model = SimpleModel(name="Test", created_at=past_dt)
    assert is_adr011_compliant(model.created_at)
    
    # Test with days_from_now
    future_dt = days_from_now(7)
    model = SimpleModel(name="Test", created_at=future_dt)
    assert is_adr011_compliant(model.created_at)
    
    # Test with ensure_utc
    naive_dt = datetime.utcnow()
    model = SimpleModel(name="Test", created_at=ensure_utc(naive_dt))
    assert is_adr011_compliant(model.created_at)
