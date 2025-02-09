from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Import all models to ensure they're registered with Base.metadata
from ..models.transactions import AccountTransaction
from ..models.accounts import Account
from ..models.bill_splits import BillSplit
from ..models.bills import Bill
from ..models.recurring_bills import RecurringBill
from ..models.income import Income
from ..models.cashflow import CashflowForecast

__all__ = [
    "Base",
    "AccountTransaction",
    "Account",
    "BillSplit",
    "Bill",
    "RecurringBill",
    "Income",
    "CashflowForecast"
]
