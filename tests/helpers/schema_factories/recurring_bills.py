"""
Recurring bill schema factory functions.

This module provides factory functions for creating valid RecurringBill-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.recurring_bills import RecurringBillCreate
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function


@factory_function(RecurringBillCreate)
def create_recurring_bill_schema(
    account_id: int,
    category_id: int,
    bill_name: str = "Test Monthly Bill",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    auto_pay: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringBillCreate schema instance.

    Args:
        account_id: ID of the account associated with this bill
        category_id: ID of the category associated with this bill
        bill_name: Name of the recurring bill
        amount: Amount of the recurring bill (defaults to 100.00)
        day_of_month: Day of the month when the bill is due (1-31)
        auto_pay: Whether the bill is set up for automatic payment
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringBillCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "account_id": account_id,
        "category_id": category_id,
        "bill_name": bill_name,
        "amount": amount,
        "day_of_month": day_of_month,
        "auto_pay": auto_pay,
        **kwargs,
    }

    return data
