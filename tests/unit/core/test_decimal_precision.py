"""Tests for the decimal precision core module."""

from decimal import Decimal

import pytest

from src.utils.decimal_precision import DecimalPrecision


class TestDecimalPrecision:
    """Test cases for the DecimalPrecision class."""

    def test_round_for_display(self):
        """Test rounding to 2 decimal places for display."""
        # Test rounding down
        assert DecimalPrecision.round_for_display(Decimal("10.124")) == Decimal("10.12")

        # Test rounding up
        assert DecimalPrecision.round_for_display(Decimal("10.125")) == Decimal("10.13")

        # Test already at 2 decimal places
        assert DecimalPrecision.round_for_display(Decimal("10.10")) == Decimal("10.10")

        # Test with more than 2 decimal places that round to same value
        assert DecimalPrecision.round_for_display(Decimal("10.12499")) == Decimal(
            "10.12"
        )

    def test_round_for_calculation(self):
        """Test rounding to 4 decimal places for internal calculations."""
        # Test rounding down
        assert DecimalPrecision.round_for_calculation(Decimal("10.12345")) == Decimal(
            "10.1235"
        )

        # Test rounding up
        assert DecimalPrecision.round_for_calculation(Decimal("10.12345")) == Decimal(
            "10.1235"
        )

        # Test already at 4 decimal places
        assert DecimalPrecision.round_for_calculation(Decimal("10.1234")) == Decimal(
            "10.1234"
        )

        # Test with more than 4 decimal places that round to same value
        assert DecimalPrecision.round_for_calculation(Decimal("10.123449")) == Decimal(
            "10.1234"
        )

    def test_validate_input_precision(self):
        """Test validation of input precision."""
        # Test 0 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal("10")) is True

        # Test 1 decimal place
        assert DecimalPrecision.validate_input_precision(Decimal("10.1")) is True

        # Test 2 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal("10.12")) is True

        # Test 3 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal("10.123")) is False

        # Test 4 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal("10.1234")) is False

    def test_distribute_with_largest_remainder_even_split(self):
        """Test distribution with no remainder."""
        total = Decimal("100.00")
        parts = 4

        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

        # Check that each part is 25.00
        assert all(part == Decimal("25.00") for part in result)

        # Check that the sum is exactly the original total
        assert sum(result) == total

        # Check that we have the correct number of parts
        assert len(result) == parts

    def test_distribute_with_largest_remainder_uneven_split(self):
        """Test distribution with a remainder."""
        total = Decimal("100.00")
        parts = 3

        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

        # Check that we have the expected parts
        expected = [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
        assert result == expected

        # Check that the sum is exactly the original total
        assert sum(result) == total

        # Check that we have the correct number of parts
        assert len(result) == parts

        # Check maximum difference between any two parts
        max_diff = max(result) - min(result)
        assert max_diff == Decimal(
            "0.01"
        ), "The maximum difference should be exactly 1 cent"

    def test_distribute_with_largest_remainder_odd_amount(self):
        """Test distribution with a non-round total amount."""
        total = Decimal("99.99")
        parts = 2

        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

        # Check that we have the expected parts
        expected = [Decimal("50.00"), Decimal("49.99")]
        assert result == expected

        # Check that the sum is exactly the original total
        assert sum(result) == total

    def test_distribute_by_percentage_exact(self):
        """Test percentage-based distribution with exact percentages."""
        total = Decimal("100.00")
        percentages = [Decimal("50"), Decimal("30"), Decimal("20")]

        result = DecimalPrecision.distribute_by_percentage(total, percentages)

        # Check that we have the expected parts
        expected = [Decimal("50.00"), Decimal("30.00"), Decimal("20.00")]
        assert result == expected

        # Check that the sum is exactly the original total
        assert sum(result) == total

    def test_distribute_by_percentage_with_rounding(self):
        """Test percentage-based distribution with rounding needed."""
        total = Decimal("100.00")
        percentages = [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]

        result = DecimalPrecision.distribute_by_percentage(total, percentages)

        # Verify the expected result matches a specific distribution
        # Should match [33.33, 33.33, 33.34] or something similar with exact sum
        assert sum(result) == total

        # Check that the distribution is reasonable (close to expected percentages)
        assert Decimal("33.00") <= result[0] <= Decimal("34.00")
        assert Decimal("33.00") <= result[1] <= Decimal("34.00")
        assert Decimal("33.00") <= result[2] <= Decimal("34.00")

        # Verify exactly 2 decimal places in all results
        for amount in result:
            assert (
                amount.as_tuple().exponent == -2
            ), f"{amount} should have exactly 2 decimal places"

    def test_distribute_by_percentage_with_four_decimal_precision(self):
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

    def test_distribute_by_percentage_invalid_sum(self):
        """Test that an error is raised when percentages don't sum to 100%."""
        total = Decimal("100.00")
        percentages = [Decimal("50"), Decimal("30"), Decimal("25")]  # Sums to 105%

        with pytest.raises(ValueError) as excinfo:
            DecimalPrecision.distribute_by_percentage(total, percentages)

        assert "Percentages must sum to 100%" in str(excinfo.value)

    def test_split_bill_amount(self):
        """Test the split_bill_amount convenience method."""
        total = Decimal("100.00")
        splits = 3

        result = DecimalPrecision.split_bill_amount(total, splits)

        # Should be the same as distribute_with_largest_remainder
        expected = DecimalPrecision.distribute_with_largest_remainder(total, splits)
        assert result == expected

        # Check that the sum is exactly the original total
        assert sum(result) == total

        # Check that we have the correct number of splits
        assert len(result) == splits

    def test_split_one_hundred_three_ways(self):
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

    def test_common_bill_amounts(self):
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

    def test_large_amount_distribution(self):
        """Test distribution of large monetary amounts."""
        total = Decimal("9999999.99")  # Very large amount
        parts = 7

        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)

        # Check sum equals total
        assert sum(result) == total

        # Check all amounts have 2 decimal places
        for amount in result:
            assert amount.as_tuple().exponent == -2

    def test_validate_sum_equals_total(self):
        """Test the validate_sum_equals_total method."""

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

        # Test with empty list
        assert DecimalPrecision.validate_sum_equals_total([], Decimal("0.00")) is True

        # Test with empty list and non-zero total
        assert (
            DecimalPrecision.validate_sum_equals_total([], Decimal("100.00")) is False
        )
