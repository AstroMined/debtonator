from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Date, Numeric, Index, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..database.base import Base

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
    payment_sources: Mapped[List["PaymentSource"]] = relationship(
        "PaymentSource",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    bills: Mapped[List["Bill"]] = relationship("Bill", back_populates="account")
    bill_splits: Mapped[List["BillSplit"]] = relationship(
        "BillSplit",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    income: Mapped[List["Income"]] = relationship("Income", back_populates="account")
    recurring_bills: Mapped[List["RecurringBill"]] = relationship(
        "RecurringBill",
        back_populates="account"
    )

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

    @validates('available_balance')
    def validate_balance(self, key: str, value: Decimal) -> Decimal:
        """Validate and update available credit when balance changes"""
        if hasattr(self, 'type') and self.type == "credit" and hasattr(self, 'total_limit') and self.total_limit is not None:
            self.available_credit = self.total_limit - abs(value)
        return value

# Set up event listeners
@event.listens_for(Account, 'after_insert')
def receive_after_insert(mapper, connection, target):
    target.update_available_credit()

@event.listens_for(Account, 'after_update')
def receive_after_update(mapper, connection, target):
    target.update_available_credit()
