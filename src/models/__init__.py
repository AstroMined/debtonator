"""
Database models for the application.

This module provides SQLAlchemy ORM models representing database tables
and relationships. Models are purely data-focused with no business logic
as per architectural guidelines.
"""

# isort: skip_file
# Imports must maintain this specific order to resolve circular dependencies

# Import Base classes first
from src.models.base_model import BaseDBModel

# Import independent models with no relationships first
from src.models.feature_flags import FeatureFlag

# Import models with relationships in dependency order
from src.models.categories import Category
from src.models.accounts import Account
from src.models.income_categories import IncomeCategory
from src.models.liabilities import Liability, LiabilityStatus
from src.models.bill_splits import BillSplit
from src.models.payments import Payment, PaymentSource
from src.models.recurring_bills import RecurringBill
from src.models.income import Income
from src.models.recurring_income import RecurringIncome
from src.models.statement_history import StatementHistory
from src.models.credit_limit_history import CreditLimitHistory
from src.models.transaction_history import TransactionHistory
from src.models.balance_reconciliation import BalanceReconciliation
from src.models.payment_schedules import PaymentSchedule
from src.models.deposit_schedules import DepositSchedule
from src.models.balance_history import BalanceHistory
from src.models.cashflow import CashflowForecast

# Ensure all models are accessible from models package
__all__ = [
    "BaseDBModel",
    "Category",
    "Account",
    "Liability",
    "LiabilityStatus",
    "BillSplit",
    "Payment",
    "PaymentSource",
    "RecurringBill",
    "Income",
    "IncomeCategory",
    "RecurringIncome",
    "StatementHistory",
    "CreditLimitHistory",
    "TransactionHistory",
    "BalanceReconciliation",
    "PaymentSchedule",
    "DepositSchedule",
    "BalanceHistory",
    "CashflowForecast",
    "FeatureFlag",
]
