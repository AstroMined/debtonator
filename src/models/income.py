from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import String, DateTime, Boolean, Numeric, Index, ForeignKey, CheckConstraint
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel

class Income(BaseDBModel):
    """
    Income model representing an income record.
    
    All datetime fields are stored in UTC format, with timezone validation enforced
    through Pydantic schemas.
    """
    __tablename__ = "income"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        doc="UTC timestamp of when the income was received"
    )
    source: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    deposited: Mapped[bool] = mapped_column(Boolean, default=False)
    undeposited_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        comment="Calculated field for undeposited amounts"
    )
    # Account and Category relationships
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="income")
    category_id: Mapped[int] = mapped_column(ForeignKey("income_categories.id"), nullable=True)
    category = relationship("IncomeCategory")

    # Recurring Income relationship
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_income_id: Mapped[int] = mapped_column(ForeignKey("recurring_income.id"), nullable=True)
    recurring_income = relationship("RecurringIncome", back_populates="income_entries")

    # Payment and Schedule Relationships
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="income")
    deposit_schedules: Mapped[List["DepositSchedule"]] = relationship("DepositSchedule", back_populates="income")

    # Create indexes and constraints
    __table_args__ = (
        Index('idx_income_date', 'date'),
        Index('idx_income_deposited', 'deposited'),
        CheckConstraint('amount >= 0', name='ck_income_positive_amount'),
    )

    def __repr__(self) -> str:
        return f"<Income {self.source} {self.amount}>"

    def calculate_undeposited(self) -> None:
        """Calculate undeposited amount based on deposit status"""
        self.undeposited_amount = self.amount if not self.deposited else Decimal(0)
