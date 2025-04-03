from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseDBModel


class Account(BaseDBModel):
    """
    Account model representing a financial account.

    This is a polymorphic base class using SQLAlchemy's joined table inheritance.
    The account_type field acts as the discriminator to determine the concrete type.

    This is a pure data structure model with no business logic (ADR-012 compliant).
    All business logic, such as available_credit calculations and validation,
    is handled by the AccountService.

    All datetime fields are stored as naive datetimes in UTC (ADR-011 compliant).
    Timezone validation is enforced through Pydantic schemas.

    Implemented as part of ADR-016 Account Type Expansion.
    """

    __tablename__ = "accounts"

    # Primary key and basic fields
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type of account - discriminator for polymorphic identity",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Optional description for the account",
    )

    # Balance and credit fields
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="Current balance"
    )
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="Available balance"
    )

    # New fields for ADR-016
    institution: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Financial institution for the account"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="ISO 4217 currency code (e.g., USD, EUR, GBP)",
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether the account is closed"
    )
    account_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Account number (may be masked for security)"
    )
    url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="URL for the account's web portal"
    )
    logo_path: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Path to the account's logo image"
    )

    # Action tracking for performance optimization
    next_action_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),
        nullable=True,
        comment="Date of next required action (payment due, etc.)",
    )
    next_action_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Amount associated with next action"
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

    # SQLAlchemy polymorphic mapping
    __mapper_args__ = {
        "polymorphic_identity": "account",
        "polymorphic_on": account_type,
    }

    # Create indexes for efficient lookups
    __table_args__ = (
        Index("idx_accounts_name", "name"),
        Index("idx_accounts_type", account_type),
        Index("idx_accounts_is_closed", is_closed),
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name={self.name}, type={self.account_type})>"


# Concrete account type models will be implemented in separate files as part of ADR-019
