from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Date, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base
from .transactions import AccountTransaction
from .bill_splits import BillSplit

class Bill(Base):
    """Bill model representing a bill payment record"""
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[str] = mapped_column(String(10))
    day_of_month: Mapped[int]
    due_date: Mapped[date]
    paid_date: Mapped[Optional[date]]
    bill_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    up_to_date: Mapped[bool] = mapped_column(Boolean, default=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account_name: Mapped[str] = mapped_column(String(50))  # Denormalized for historical data
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    transactions = relationship("AccountTransaction", back_populates="bill")
    account = relationship("Account", back_populates="bills")
    splits: Mapped[List[BillSplit]] = relationship("BillSplit", back_populates="bill", cascade="all, delete-orphan")

    # Create indexes for efficient lookups
    __table_args__ = (
        Index('idx_bills_due_date', 'due_date'),
        Index('idx_bills_paid_date', 'paid_date'),
        Index('idx_bills_account_id', 'account_id'),
        Index('idx_bills_account_name', 'account_name'),
    )

    def __repr__(self) -> str:
        return f"<Bill {self.bill_name} due {self.due_date}>"
