from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base
from .transactions import AccountTransaction
from .recurring_bills import RecurringBill

class Account(Base):
    """Account model representing a financial account"""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    type: Mapped[str] = mapped_column(
        String(20),
        comment="Type of account (credit, checking, savings)"
    )
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        comment="Current available balance"
    )
    available_credit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Available credit for credit accounts"
    )
    total_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Total credit limit for credit accounts"
    )
    last_statement_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Balance from last statement"
    )
    last_statement_date: Mapped[Optional[date]]
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    transactions = relationship("AccountTransaction", back_populates="account")
    recurring_bills = relationship("RecurringBill", back_populates="account")
    bills = relationship("Bill", back_populates="account")

    # Create indexes for efficient lookups
    __table_args__ = (
        Index('idx_accounts_name', 'name'),
    )

    def __repr__(self) -> str:
        return f"<Account {self.name}>"

    def update_available_credit(self) -> None:
        """Update available credit based on total limit and current balance"""
        if self.type == "credit" and self.total_limit is not None:
            self.available_credit = self.total_limit - abs(self.available_balance)
