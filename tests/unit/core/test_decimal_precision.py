"""Tests for the decimal precision core module."""

import pytest
from decimal import Decimal
from src.core.decimal_precision import DecimalPrecision


class TestDecimalPrecision:
    """Test cases for the DecimalPrecision class."""

    def test_round_for_display(self):
        """Test rounding to 2 decimal places for display."""
        # Test rounding down
        assert DecimalPrecision.round_for_display(Decimal('10.124')) == Decimal('10.12')
        
        # Test rounding up
        assert DecimalPrecision.round_for_display(Decimal('10.125')) == Decimal('10.13')
        
        # Test already at 2 decimal places
        assert DecimalPrecision.round_for_display(Decimal('10.10')) == Decimal('10.10')
        
        # Test with more than 2 decimal places that round to same value
        assert DecimalPrecision.round_for_display(Decimal('10.12499')) == Decimal('10.12')

    def test_round_for_calculation(self):
        """Test rounding to 4 decimal places for internal calculations."""
        # Test rounding down
        assert DecimalPrecision.round_for_calculation(Decimal('10.12345')) == Decimal('10.1235')
        
        # Test rounding up
        assert DecimalPrecision.round_for_calculation(Decimal('10.12345')) == Decimal('10.1235')
        
        # Test already at 4 decimal places
        assert DecimalPrecision.round_for_calculation(Decimal('10.1234')) == Decimal('10.1234')
        
        # Test with more than 4 decimal places that round to same value
        assert DecimalPrecision.round_for_calculation(Decimal('10.123449')) == Decimal('10.1234')

    def test_validate_input_precision(self):
        """Test validation of input precision."""
        # Test 0 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal('10')) is True
        
        # Test 1 decimal place
        assert DecimalPrecision.validate_input_precision(Decimal('10.1')) is True
        
        # Test 2 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal('10.12')) is True
        
        # Test 3 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal('10.123')) is False
        
        # Test 4 decimal places
        assert DecimalPrecision.validate_input_precision(Decimal('10.1234')) is False

    def test_distribute_with_largest_remainder_even_split(self):
        """Test distribution with no remainder."""
        total = Decimal('100.00')
        parts = 4
        
        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)
        
        # Check that each part is 25.00
        assert all(part == Decimal('25.00') for part in result)
        
        # Check that the sum is exactly the original total
        assert sum(result) == total
        
        # Check that we have the correct number of parts
        assert len(result) == parts

    def test_distribute_with_largest_remainder_uneven_split(self):
        """Test distribution with a remainder."""
        total = Decimal('100.00')
        parts = 3
        
        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)
        
        # Check that we have the expected parts
        expected = [Decimal('33.34'), Decimal('33.33'), Decimal('33.33')]
        assert result == expected
        
        # Check that the sum is exactly the original total
        assert sum(result) == total
        
        # Check that we have the correct number of parts
        assert len(result) == parts

    def test_distribute_with_largest_remainder_odd_amount(self):
        """Test distribution with a non-round total amount."""
        total = Decimal('99.99')
        parts = 2
        
        result = DecimalPrecision.distribute_with_largest_remainder(total, parts)
        
        # Check that we have the expected parts
        expected = [Decimal('50.00'), Decimal('49.99')]
        assert result == expected
        
        # Check that the sum is exactly the original total
        assert sum(result) == total

    def test_distribute_by_percentage_exact(self):
        """Test percentage-based distribution with exact percentages."""
        total = Decimal('100.00')
        percentages = [Decimal('50'), Decimal('30'), Decimal('20')]
        
        result = DecimalPrecision.distribute_by_percentage(total, percentages)
        
        # Check that we have the expected parts
        expected = [Decimal('50.00'), Decimal('30.00'), Decimal('20.00')]
        assert result == expected
        
        # Check that the sum is exactly the original total
        assert sum(result) == total

    def test_distribute_by_percentage_with_rounding(self):
        """Test percentage-based distribution with rounding needed."""
        total = Decimal('100.00')
        percentages = [Decimal('33.33'), Decimal('33.33'), Decimal('33.34')]
        
        result = DecimalPrecision.distribute_by_percentage(total, percentages)
        
        # Check that we have the expected parts (may vary based on implementation)
        # But the sum should be exactly the original total
        assert sum(result) == total
        
        # Check that the distribution is reasonable (close to expected percentages)
        assert Decimal('33.00') <= result[0] <= Decimal('34.00')
        assert Decimal('33.00') <= result[1] <= Decimal('34.00')
        assert Decimal('33.00') <= result[2] <= Decimal('34.00')

    def test_distribute_by_percentage_invalid_sum(self):
        """Test that an error is raised when percentages don't sum to 100%."""
        total = Decimal('100.00')
        percentages = [Decimal('50'), Decimal('30'), Decimal('25')]  # Sums to 105%
        
        with pytest.raises(ValueError) as excinfo:
            DecimalPrecision.distribute_by_percentage(total, percentages)
        
        assert "Percentages must sum to 100%" in str(excinfo.value)

    def test_split_bill_amount(self):
        """Test the split_bill_amount convenience method."""
        total = Decimal('100.00')
        splits = 3
        
        result = DecimalPrecision.split_bill_amount(total, splits)
        
        # Should be the same as distribute_with_largest_remainder
        expected = DecimalPrecision.distribute_with_largest_remainder(total, splits)
        assert result == expected
        
        # Check that the sum is exactly the original total
        assert sum(result) == total
        
        # Check that we have the correct number of splits
        assert len(result) == splits
