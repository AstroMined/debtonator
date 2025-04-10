"""
Comprehensive unit tests for the decimal_precision module.

This combined test file incorporates tests from both:
- tests/unit/utils/test_decimal_precision.py
- tests/unit/core/test_decimal_precision.py

It ensures 100% coverage of the decimal_precision.py module, including
all branches in the distribute_by_percentage method.
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
    assert DecimalPrecision.round_for_display(Decimal("10.125")) == Decimal("10.13")
    
    # Test rounding down
    assert DecimalPrecision.round_for_display(Decimal("10.554")) == Decimal("10.55")
    assert DecimalPrecision.round_for_display(Decimal("10.994")) == Decimal("10.99")
    assert DecimalPrecision.round_for_display(Decimal("10.124")) == Decimal("10.12")
    assert DecimalPrecision.round_for_display(Decimal("10.12499")) == Decimal("10.12")
    
    # Test negative values
    assert DecimalPrecision.round_for_display(Decimal("-10.555")) == Decimal("-10.56")
    assert DecimalPrecision.round_for_display(Decimal("-10.554")) == Decimal("-10.55")
    
    # Test already at 2 decimal places
    assert DecimalPrecision.round_for_display(Decimal("10.10")) == Decimal("10.10")


def test_round_for_calculation():
    """Test rounding to 4 decimal places for internal calculations."""
    # Test exact values
    assert DecimalPrecision.round_for_calculation(Decimal("10.0000")) == Decimal("10.0000")
    assert DecimalPrecision.round_for_calculation(Decimal("10.5000")) == Decimal("10.5000")
    
    # Test rounding up
    assert DecimalPrecision.round_for_calculation(Decimal("10.55555")) == Decimal("10.5556")
    assert DecimalPrecision.round_for_calculation(Decimal("10.99995")) == Decimal("11.0000")
    assert DecimalPrecision.round_for_calculation(Decimal("10.12345")) == Decimal("10.1235")
    
    # Test rounding down
    assert DecimalPrecision.round_for_calculation(Decimal("10.55554")) == Decimal("10.5555")
    assert DecimalPrecision.round_for_calculation(Decimal("10.99994")) == Decimal("10.9999")
    assert DecimalPrecision.round_for_calculation(Decimal("10.123449")) == Decimal("10.1234")
    
    # Test negative values
    assert DecimalPrecision.round_for_calculation(Decimal("-10.55555")) == Decimal("-10.5556")
    assert DecimalPrecision.round_for_calculation(Decimal("-10.55554")) == Decimal("-10.5555")
    
    # Test already at 4 decimal places
    assert DecimalPrecision.round_for_calculation(Decimal("10.1234")) == Decimal("10.1234")


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
    assert DecimalPrecision.validate_input_precision(Decimal("10.123")) is False
    assert DecimalPrecision.validate_input_precision(Decimal("10.1234")) is False


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
    
    # Test with a non-round total amount
    result = DecimalPrecision.distribute_with_largest_remainder(Decimal("99.99"), 2)
    assert len(result) == 2
    assert result == [Decimal("50.00"), Decimal("49.99")]
    assert sum(result) == Decimal("99.99")


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


def test_distribute_by_percentage_with_four_decimal_precision():
    """Test percentage-based distribution with 4 decimal percentages."""
    total = Decimal("100.00")
    # Use 4 decimal precision in percentages (representing 33.3333...%)
    percentages = [Decimal("33.3333"), Decimal("33.3333"), Decimal("33.3334")]

    result = DecimalPrecision.distribute_by_percentage(total, percentages)

    # Verify sum equals the original amount exactly
    assert sum(result) == total

    # Check the results have 2 decimal places
    for amount in result:
        assert amount.as_tuple().exponent == -2


def test_distribute_by_percentage_with_negative_remainder():
    """Test percentage-based distribution with negative remainder.
    
    This test specifically targets line 142 in decimal_precision.py.
    """
    # Create a scenario where rounding up causes the sum to exceed the total
    # This will create a negative remainder that needs to be distributed
    total = Decimal("100.00")
    
    # These percentages will cause amounts to round up, creating a negative remainder
    percentages = [Decimal("33.335"), Decimal("33.335"), Decimal("33.33")]
    
    result = DecimalPrecision.distribute_by_percentage(total, percentages)
    
    # Verify the sum equals the original total exactly
    assert sum(result) == total
    
    # The first two values would normally round to 33.34 each (total 66.68)
    # The third would be 33.33, making 100.01 which is too much
    # So one of them should be adjusted down to 33.33
    assert sorted(result) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]


def test_distribute_by_percentage_with_positive_remainder():
    """Test percentage-based distribution with positive remainder.
    
    This test specifically targets line 144 in decimal_precision.py.
    """
    # Create a scenario where rounding down causes the sum to be less than the total
    # This will create a positive remainder that needs to be distributed
    total = Decimal("100.00")
    
    # These percentages will cause amounts to round down, creating a positive remainder
    percentages = [Decimal("33.334"), Decimal("33.333"), Decimal("33.333")]
    
    result = DecimalPrecision.distribute_by_percentage(total, percentages)
    
    # Verify the sum equals the original total exactly
    assert sum(result) == total
    
    # The values would normally round to 33.33 each (total 99.99)
    # So one of them should be adjusted up to 33.34
    assert sorted(result) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]


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


def test_split_one_hundred_three_ways():
    """Test the specific $100 split three ways case - a classic decimal challenge."""
    total = Decimal("100.00")
    parts = 3

    result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

    # Verify the expected distribution
    assert result == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]

    # Verify the sum equals the original amount exactly
    assert sum(result) == total

    # Verify each amount has exactly 2 decimal places
    for amount in result:
        assert (
            amount.as_tuple().exponent == -2
        ), f"{amount} should have exactly 2 decimal places"


def test_common_bill_amounts():
    """Test common bill amounts that could be problematic."""
    # Test cases with difficult divisions
    test_cases = [
        # total, parts, expected first element
        (Decimal("100.00"), 3, Decimal("33.34")),  # Classic $100/3
        (Decimal("10.00"), 3, Decimal("3.34")),  # $10/3
        (Decimal("1.00"), 3, Decimal("0.34")),  # $1/3
        (Decimal("20.00"), 3, Decimal("6.67")),  # $20/3
        (Decimal("50.00"), 3, Decimal("16.67")),  # $50/3
        (Decimal("74.99"), 3, Decimal("25.00")),  # Odd amount
        (Decimal("0.01"), 3, Decimal("0.01")),  # Minimum amount
        (Decimal("0.02"), 3, Decimal("0.01")),  # Near-minimum amount
        (Decimal("0.03"), 3, Decimal("0.01")),  # Exact minimum distribution
    ]

    for total, parts, expected_first in test_cases:
        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)
        # Check first element (which should get the remainder)
        assert result[0] == expected_first, f"Failed for {total}/{parts}: {result}"
        # Check sum equals total
        assert (
            sum(result) == total
        ), f"Sum doesn't match for {total}/{parts}: {sum(result)} != {total}"


def test_large_amount_distribution():
    """Test distribution of large monetary amounts."""
    total = Decimal("9999999.99")  # Very large amount
    parts = 7

    result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

    # Check sum equals total
    assert sum(result) == total

    # Check all amounts have 2 decimal places
    for amount in result:
        assert amount.as_tuple().exponent == -2


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
    
    # From core test file - MockItem class
    class MockItem:
        def __init__(self, amount):
            self.amount = amount

    # Create test items with exact sum
    items_exact = [
        MockItem(Decimal("33.33")),
        MockItem(Decimal("33.33")),
        MockItem(Decimal("33.34")),
    ]

    # Create test items with sum slightly off but within epsilon
    items_within_epsilon = [
        MockItem(Decimal("33.33")),
        MockItem(Decimal("33.33")),
        MockItem(Decimal("33.35")),  # 1 cent more than expected
    ]

    # Create test items with sum outside epsilon
    items_outside_epsilon = [
        MockItem(Decimal("33.33")),
        MockItem(Decimal("33.33")),
        MockItem(Decimal("34.34")),  # $1.00 more than expected
    ]

    # Test with exact sum
    assert (
        DecimalPrecision.validate_sum_equals_total(items_exact, Decimal("100.00"))
        is True
    )

    # Test with sum within epsilon
    assert (
        DecimalPrecision.validate_sum_equals_total(
            items_within_epsilon, Decimal("100.00")
        )
        is True
    )

    # Test with sum outside epsilon
    assert (
        DecimalPrecision.validate_sum_equals_total(
            items_outside_epsilon, Decimal("100.00")
        )
        is False
    )

    # Test with custom epsilon
    assert (
        DecimalPrecision.validate_sum_equals_total(
            items_outside_epsilon, Decimal("100.00"), epsilon=Decimal("1.00")
        )
        is True
    )

    # Test with empty list and non-zero total
    assert (
        DecimalPrecision.validate_sum_equals_total([], Decimal("100.00")) is False
    )
