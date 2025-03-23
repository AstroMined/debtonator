from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .balance_history import BalanceHistory
from .balance_reconciliation import BalanceReconciliation
from .base_model import BaseDBModel
from .bill_splits import BillSplit
from .credit_limit_history import CreditLimitHistory
from .deposit_schedules import DepositSchedule
from .income import Income
from .liabilities import Liability
from .payment_schedules import PaymentSchedule
from .payments import PaymentSource
from .recurring_bills import RecurringBill
from .recurring_income import RecurringIncome
from .statement_history import StatementHistory
from .transaction_history import TransactionHistory


class Account(BaseDBModel):
    """
    Account model representing a financial account.

    This is a pure data structure model with no business logic (ADR-012 compliant).
    All business logic, such as available_credit calculations and validation,
    is handled by the AccountService.

    All datetime fields are stored as naive datetimes in UTC (ADR-011 compliant).
    Timezone validation is enforced through Pydantic schemas.
    """

    __tablename__ = "accounts"

    # Primary key and basic fields
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type of account (credit, checking, savings)",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Optional description for the account",
    )

    # Balance and credit fields
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="Current available balance"
    )
    available_credit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Available credit for credit accounts"
    )
    total_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Total credit limit for credit accounts"
    )

    # Statement fields
    last_statement_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Balance from last statement"
    )
    last_statement_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        nullable=True,
        doc="UTC timestamp of the last statement date",
    )

    # Relationships
    payment_sources: Mapped[List["PaymentSource"]] = relationship(
        "PaymentSource", back_populates="account", cascade="all, delete-orphan"
    )
    liabilities: Mapped[List["Liability"]] = relationship(
        "Liability",
        foreign_keys="[Liability.primary_account_id]",
        back_populates="primary_account",
    )
    bill_splits: Mapped[List["BillSplit"]] = relationship(
        "BillSplit", back_populates="account", cascade="all, delete-orphan"
    )
    income: Mapped[List["Income"]] = relationship("Income", back_populates="account")
    recurring_bills: Mapped[List["RecurringBill"]] = relationship(
        "RecurringBill", back_populates="account"
    )
    recurring_income: Mapped[List["RecurringIncome"]] = relationship(
        "RecurringIncome", back_populates="account", cascade="all, delete-orphan"
    )
    statement_history: Mapped[List["StatementHistory"]] = relationship(
        "StatementHistory", back_populates="account", cascade="all, delete-orphan"
    )
    credit_limit_history: Mapped[List["CreditLimitHistory"]] = relationship(
        "CreditLimitHistory", back_populates="account", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["TransactionHistory"]] = relationship(
        "TransactionHistory", back_populates="account", cascade="all, delete-orphan"
    )
    balance_reconciliations: Mapped[List["BalanceReconciliation"]] = relationship(
        "BalanceReconciliation", back_populates="account", cascade="all, delete-orphan"
    )
    payment_schedules: Mapped[List["PaymentSchedule"]] = relationship(
        "PaymentSchedule", back_populates="account", cascade="all, delete-orphan"
    )
    deposit_schedules: Mapped[List["DepositSchedule"]] = relationship(
        "DepositSchedule", back_populates="account", cascade="all, delete-orphan"
    )
    balance_history: Mapped[List["BalanceHistory"]] = relationship(
        "BalanceHistory", back_populates="account", cascade="all, delete-orphan"
    )

    # Create indexes for efficient lookups
    __table_args__ = (Index("idx_accounts_name", "name"),)

    def __repr__(self) -> str:
        return f"<Account {self.name}>"
