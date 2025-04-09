"""
Unit tests for the decimal_precision module.

Tests all decimal precision utility functions with a focus on:
- Rounding functions
- Validation functions
- Distribution functions
- Bill split functions
"""

from decimal import Decimal

import pytest

from src.utils.decimal_precision import DecimalPrecision


def test_round_for_display():
    """Test rounding to 2 decimal places for display."""
    # Test exact values
    assert DecimalPrecision.round_for_display(Decimal("10.00")) == Decimal("10.00")
    assert DecimalPrecision.round_for_display(Decimal("10.50")) == Decimal("10.50")
    
    # Test rounding up
    assert DecimalPrecision.round_for_display(Decimal("10.555")) == Decimal("10.56")
    assert DecimalPrecision.round_for_display(Decimal("10.995")) == Decimal("11.00")
    
    # Test rounding down
    assert DecimalPrecision.round_for_display(Decimal("10.554")) == Decimal("10.55")
    assert DecimalPrecision.round_for_display(Decimal("10.994")) == Decimal("10.99")
    
    # Test negative values
    assert DecimalPrecision.round_for_display(Decimal("-10.555")) == Decimal("-10.56")
    assert DecimalPrecision.round_for_display(Decimal("-10.554")) == Decimal("-10.55")


def test_round_for_calculation():
    """Test rounding to 4 decimal places for internal calculations."""
    # Test exact values
    assert DecimalPrecision.round_for_calculation(Decimal("10.0000")) == Decimal("10.0000")
    assert DecimalPrecision.round_for_calculation(Decimal("10.5000")) == Decimal("10.5000")
    
    # Test rounding up
    assert DecimalPrecision.round_for_calculation(Decimal("10.55555")) == Decimal("10.5556")
    assert DecimalPrecision.round_for_calculation(Decimal("10.99995")) == Decimal("11.0000")
    
    # Test rounding down
    assert DecimalPrecision.round_for_calculation(Decimal("10.55554")) == Decimal("10.5555")
    assert DecimalPrecision.round_for_calculation(Decimal("10.99994")) == Decimal("10.9999")
    
    # Test negative values
    assert DecimalPrecision.round_for_calculation(Decimal("-10.55555")) == Decimal("-10.5556")
    assert DecimalPrecision.round_for_calculation(Decimal("-10.55554")) == Decimal("-10.5555")


def test_validate_input_precision():
    """Test validation of input precision."""
    # Valid cases (0, 1, 2 decimal places)
    assert DecimalPrecision.validate_input_precision(Decimal("10")) is True
    assert DecimalPrecision.validate_input_precision(Decimal("10.5")) is True
    assert DecimalPrecision.validate_input_precision(Decimal("10.55")) is True
    
    # Invalid cases (3+ decimal places)
    assert DecimalPrecision.validate_input_precision(Decimal("10.555")) is False
    assert DecimalPrecision.validate_input_precision(Decimal("10.5555")) is False
    assert DecimalPrecision.validate_input_precision(Decimal("10.55555")) is False


def test_distribute_with_largest_remainder():
    """Test distribution with largest remainder method."""
    # Even distribution (no remainder)
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("100"), 4)
    assert len(result) == 4
    assert all(amount == Decimal("25") for amount in result)
    assert sum(result) == Decimal("100")
    
    # Uneven distribution with remainder
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("100"), 3)
    assert len(result) == 3
    # First part gets the extra cent
    assert result[0] == Decimal("33.34")
    assert result[1] == Decimal("33.33")
    assert result[2] == Decimal("33.33")
    assert sum(result) == Decimal("100")
    
    # Larger remainder
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("100"), 6)
    assert len(result) == 6
    # First 4 parts get the extra cents
    assert result[0] == Decimal("16.67")
    assert result[1] == Decimal("16.67")
    assert result[2] == Decimal("16.67")
    assert result[3] == Decimal("16.67")
    assert result[4] == Decimal("16.66")
    assert result[5] == Decimal("16.66")
    assert sum(result) == Decimal("100")
    
    # Edge case: 1 part
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("100"), 1)
    assert len(result) == 1
    assert result[0] == Decimal("100")
    
    # Edge case: 0 amount
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("0"), 4)
    assert len(result) == 4
    assert all(amount == Decimal("0") for amount in result)
    assert sum(result) == Decimal("0")


def test_distribute_by_percentage():
    """Test percentage-based distribution."""
    # Simple percentages (50%, 30%, 20%)
    percentages = [Decimal("50"), Decimal("30"), Decimal("20")]
    result = DecimalPrecision.distribute_by_percentage(Decimal("100"), percentages)
    assert len(result) == 3
    assert result[0] == Decimal("50")
    assert result[1] == Decimal("30")
    assert result[2] == Decimal("20")
    assert sum(result) == Decimal("100")
    
    # Complex percentages with rounding issues
    percentages = [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
    result = DecimalPrecision.distribute_by_percentage(Decimal("100"), percentages)
    assert len(result) == 3
    assert sum(result) == Decimal("100")
    
    # Uneven percentages that need adjustment
    percentages = [Decimal("33.33"), Decimal("33.33"), Decimal("33.33")]  # Sum is 99.99
    with pytest.raises(ValueError):
        DecimalPrecision.distribute_by_percentage(Decimal("100"), percentages)
    
    # Very small percentages
    percentages = [Decimal("0.01"), Decimal("99.99")]
    result = DecimalPrecision.distribute_by_percentage(Decimal("100"), percentages)
    assert len(result) == 2
    assert result[0] == Decimal("0.01")
    assert result[1] == Decimal("99.99")
    assert sum(result) == Decimal("100")


def test_distribute_by_percentage_with_rounding():
    """Test percentage-based distribution with rounding challenges."""
    # Test with a value that would cause rounding issues
    total = Decimal("123.45")
    percentages = [Decimal("50"), Decimal("30"), Decimal("20")]
    
    result = DecimalPrecision.distribute_by_percentage(total, percentages)
    
    # Check individual values are properly rounded
    # Note: The exact values may vary slightly due to rounding implementation
    # The important part is that they sum to the original total
    assert result[0] == Decimal("61.72") or result[0] == Decimal("61.73")  # ~50% of 123.45
    assert result[1] == Decimal("37.04") or result[1] == Decimal("37.03")  # ~30% of 123.45
    assert result[2] == Decimal("24.69") or result[2] == Decimal("24.68")  # ~20% of 123.45
    
    # Most importantly, the sum should exactly match the original total
    assert sum(result) == total


def test_split_bill_amount():
    """Test bill splitting functionality."""
    # Test with various inputs
    result = DecimalPrecision.split_bill_amount(Decimal("100"), 4)
    assert len(result) == 4
    assert all(amount == Decimal("25") for amount in result)
    assert sum(result) == Decimal("100")
    
    # Test with uneven split
    result = DecimalPrecision.split_bill_amount(Decimal("100"), 3)
    assert len(result) == 3
    assert sum(result) == Decimal("100")
    
    # Verify it calls distribute_with_largest_remainder (indirectly by checking result pattern)
    result1 = DecimalPrecision.split_bill_amount(Decimal("100"), 3)
    result2 = DecimalPrecision.distribute_with_largest_remainder(Decimal("100"), 3)
    assert result1 == result2


class TestItem:
    """Test class for validate_sum_equals_total testing."""
    
    def __init__(self, amount):
        self.amount = amount


def test_validate_sum_equals_total():
    """Test sum validation with different epsilon values."""
    # Create test items
    items = [TestItem(Decimal("10")), TestItem(Decimal("20")), TestItem(Decimal("30"))]
    
    # Test with exact match
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("60")) is True
    
    # Test with default epsilon (0.01)
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("60.005")) is True
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("59.995")) is True
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("60.02")) is False
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("59.98")) is False
    
    # Test with custom epsilon
    custom_epsilon = Decimal("0.1")
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("60.05"), epsilon=custom_epsilon) is True
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("59.95"), epsilon=custom_epsilon) is True
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("60.2"), epsilon=custom_epsilon) is False
    assert DecimalPrecision.validate_sum_equals_total(items, Decimal("59.8"), epsilon=custom_epsilon) is False
    
    # Test with empty list
    assert DecimalPrecision.validate_sum_equals_total([], Decimal("0")) is True
    # Empty list sum is 0, so anything non-zero should be false
    assert DecimalPrecision.validate_sum_equals_total([], Decimal("0.005")) is False
    assert DecimalPrecision.validate_sum_equals_total([], Decimal("0.02")) is False
    
    # Test with custom attribute name (object attributes)
    class CustomItem:
        def __init__(self, value):
            self.value = value
            
    items_custom_obj = [CustomItem(Decimal("10")), CustomItem(Decimal("20")), CustomItem(Decimal("30"))]
    assert DecimalPrecision.validate_sum_equals_total(items_custom_obj, Decimal("60"), amount_attr="value") is True
    
    # Test with dictionary keys
    items_custom_dict = [{"value": Decimal("10")}, {"value": Decimal("20")}, {"value": Decimal("30")}]
    assert DecimalPrecision.validate_sum_equals_total(items_custom_dict, Decimal("60"), amount_attr="value") is True
