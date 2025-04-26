"""
Common domain types for cashflow analysis and financial calculations.

This module contains shared domain types used across different application layers
(repositories, services, and API) to ensure consistent type definitions and behavior.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Union

# Type definition for date/datetime parameters
DateType = Union[date, datetime]


class CashflowWarningThresholds:
    """Standard warning thresholds for cashflow analysis.
    
    These thresholds are used to generate warnings and alerts in the UI
    based on financial conditions like low account balances or high
    credit utilization.
    """

    LOW_BALANCE = Decimal("100.00")  # Warning when balance drops below $100
    HIGH_CREDIT_UTILIZATION = Decimal("0.80")  # Warning at 80% credit utilization
    LARGE_OUTFLOW = Decimal("1000.00")  # Warning for outflows over $1000


class CashflowHolidays:
    """Major US holidays that might impact cashflow.
    
    Used for holiday-aware financial calculations and forecasting.
    Some financial transactions are affected by bank holidays.
    """

    def __init__(self, year: int):
        self.holidays: Dict[str, date] = {
            "new_years": date(year, 1, 1),
            "christmas": date(year, 12, 25),
            "thanksgiving": date(year, 11, 25),  # Approximate
            "tax_day": date(year, 4, 15),
        }

    def get_holidays(self) -> Dict[str, date]:
        """Get a copy of the holidays dictionary.
        
        Returns:
            Dict[str, date]: Dictionary of holiday names to dates
        """
        return self.holidays.copy()
