"""
Decimal Precision Handling module for financial calculations.

This module implements the decimal precision strategy defined in ADR-013,
providing utilities for handling monetary values with appropriate precision
throughout the application.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, List, Optional


class DecimalPrecision:
    """Utility class for handling decimal precision in financial calculations."""

    # Precision constants
    DISPLAY_PRECISION = Decimal("0.01")  # 2 decimal places
    CALCULATION_PRECISION = Decimal("0.0001")  # 4 decimal places

    # Epsilon for comparing decimal equality in financial calculations
    EPSILON = Decimal("0.01")

    @staticmethod
    def round_for_display(value: Decimal) -> Decimal:
        """
        Round to 2 decimal places for user display.

        Args:
            value: The decimal value to round

        Returns:
            Decimal value rounded to 2 decimal places
        """
        return value.quantize(
            DecimalPrecision.DISPLAY_PRECISION, rounding=ROUND_HALF_UP
        )

    @staticmethod
    def round_for_calculation(value: Decimal) -> Decimal:
        """
        Round to 4 decimal places for internal calculations.

        Args:
            value: The decimal value to round

        Returns:
            Decimal value rounded to 4 decimal places
        """
        return value.quantize(
            DecimalPrecision.CALCULATION_PRECISION, rounding=ROUND_HALF_UP
        )

    @staticmethod
    def validate_input_precision(value: Decimal) -> bool:
        """
        Validate that input has no more than 2 decimal places.

        Args:
            value: The decimal value to validate

        Returns:
            True if the value has at most 2 decimal places, False otherwise
        """
        return value.as_tuple().exponent >= -2

    @staticmethod
    def distribute_with_largest_remainder(total: Decimal, parts: int) -> List[Decimal]:
        """
        Distribute a total amount into equal parts without losing cents.

        This implementation uses the largest remainder method to ensure
        the distributed parts sum exactly to the original total.

        Args:
            total: Total amount to distribute
            parts: Number of parts to distribute into

        Returns:
            List of distributed amounts that sum exactly to the total
        """
        # Step 1: Calculate base amount (integer division)
        cents = int(total * 100)
        base_cents = cents // parts

        # Step 2: Calculate remainder
        remainder_cents = cents - (base_cents * parts)

        # Step 3: Distribute base amounts
        result = [Decimal(base_cents) / 100] * parts

        # Step 4: Distribute remainder one cent at a time
        for i in range(remainder_cents):
            result[i] += Decimal("0.01")

        return result

    @staticmethod
    def distribute_by_percentage(
        total: Decimal, percentages: List[Decimal]
    ) -> List[Decimal]:
        """
        Distribute a total amount according to percentages, ensuring the sum equals the original total.

        Args:
            total: Total amount to distribute
            percentages: List of percentages (should sum to 100%)

        Returns:
            List of distributed amounts that sum exactly to the total
        """
        # Validate percentages
        percentage_sum = sum(percentages)
        if abs(percentage_sum - Decimal("100")) > Decimal("0.0001"):
            raise ValueError(f"Percentages must sum to 100%, got {percentage_sum}%")

        # Calculate amounts with 4 decimal precision
        amounts = [total * (p / Decimal("100")) for p in percentages]

        # Round to 2 decimal places for initial allocation
        rounded = [
            amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            for amount in amounts
        ]

        # Calculate difference due to rounding
        rounded_sum = sum(rounded)
        remainder = (total - rounded_sum).quantize(Decimal("0.01"))

        # Distribute remainder using largest fractional part method
        if remainder != Decimal("0"):
            # Find indices of amounts with the largest fractional parts
            fractional_parts = [
                (i, (amounts[i] - rounded[i]).copy_abs()) for i in range(len(amounts))
            ]
            fractional_parts.sort(key=lambda x: x[1], reverse=True)

            # Add or subtract cents from amounts with the largest fractional parts
            cents_to_distribute = int(remainder * 100)
            for i in range(abs(cents_to_distribute)):
                idx = fractional_parts[i % len(fractional_parts)][0]
                if cents_to_distribute > 0:
                    rounded[idx] += Decimal("0.01")
                else:
                    rounded[idx] -= Decimal("0.01")

        return rounded

    @staticmethod
    def split_bill_amount(total: Decimal, splits: int) -> List[Decimal]:
        """
        Split a bill amount into equal parts, handling rounding appropriately.

        This is a convenience method that uses distribute_with_largest_remainder
        under the hood.

        Args:
            total: The total bill amount
            splits: Number of ways to split the bill

        Returns:
            List of equal split amounts that sum exactly to the original total
        """
        return DecimalPrecision.distribute_with_largest_remainder(total, splits)

    @staticmethod
    def validate_sum_equals_total(
        items: List[Any],
        total: Decimal,
        amount_attr: str = "amount",
        epsilon: Optional[Decimal] = None,
    ) -> bool:
        """
        Validates that a sum of values equals an expected total within a small epsilon.

        Args:
            items: List of objects with amount attributes
            total: Expected total
            amount_attr: Name of the attribute containing the amount
            epsilon: Maximum allowed difference (defaults to DecimalPrecision.EPSILON)

        Returns:
            bool: True if sum matches total within epsilon, False otherwise
        """
        if not items:
            return total == Decimal("0")

        if epsilon is None:
            epsilon = DecimalPrecision.EPSILON

        # Handle both object attributes and dictionary keys
        sum_value = sum(
            item[amount_attr] if isinstance(item, dict) else getattr(item, amount_attr)
            for item in items
        )
        return abs(sum_value - total) <= epsilon
