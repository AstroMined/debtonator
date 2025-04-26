from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Union

DateType = Union[date, datetime]


class CashflowWarningThresholds:
    """Standard warning thresholds for cashflow analysis."""

    LOW_BALANCE = Decimal("100.00")  # Warning when balance drops below $100
    HIGH_CREDIT_UTILIZATION = Decimal("0.80")  # Warning at 80% credit utilization
    LARGE_OUTFLOW = Decimal("1000.00")  # Warning for outflows over $1000


class CashflowHolidays:
    """Major US holidays that might impact cashflow."""

    def __init__(self, year: int):
        self.holidays: Dict[str, date] = {
            "new_years": date(year, 1, 1),
            "christmas": date(year, 12, 25),
            "thanksgiving": date(year, 11, 25),  # Approximate
            "tax_day": date(year, 4, 15),
        }

    def get_holidays(self) -> Dict[str, date]:
        return self.holidays.copy()
