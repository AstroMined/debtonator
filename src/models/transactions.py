from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Date, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class AccountTransaction(Base):
    """Account transaction model representing financial transactions"""
    __tablename__ = "account_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    bill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bills.id"), nullable=True)
    income_id: Mapped[Optional[int]] = mapped_column(ForeignKey("income.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    transaction_date: Mapped[date]
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    bill = relationship("Bill", back_populates="transactions")
    income = relationship("Income", back_populates="transactions")

    # Create indexes for efficient lookups
    __table_args__ = (
        Index('idx_transactions_date', 'transaction_date'),
        Index('idx_transactions_account', 'account_id'),
    )

    def __repr__(self) -> str:
        return f"<AccountTransaction {self.amount} on {self.transaction_date}>"
