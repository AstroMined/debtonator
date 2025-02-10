from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Import all models to ensure they're registered with Base.metadata
from ..models.accounts import Account
from ..models.bill_splits import BillSplit
from ..models.recurring_bills import RecurringBill
from ..models.income import Income
from ..models.cashflow import CashflowForecast
from ..models.liabilities import Liability
from ..models.payments import Payment, PaymentSource

__all__ = [
    "Base",
    "Account",
    "BillSplit",
    "RecurringBill",
    "Income",
    "CashflowForecast",
    "Liability",
    "Payment",
    "PaymentSource"
]
