from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Date, Boolean, Numeric, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base
from src.models.payment_schedules import PaymentSchedule

class LiabilityStatus(str, Enum):
    """Enum for liability status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PAID = "paid"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class Liability(Base):
    """Liability model representing a bill that needs to be paid"""
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    due_date: Mapped[date] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_bill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recurring_bills.id"), nullable=True)
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="bills")
    primary_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_pay_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For preferred payment date, method, etc.
    last_auto_pay_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    auto_pay_enabled: Mapped[bool] = mapped_column(Boolean, default=False)  # Separate from auto_pay flag for temporary enable/disable
    status: Mapped[LiabilityStatus] = mapped_column(
        SQLEnum(LiabilityStatus),
        default=LiabilityStatus.PENDING
    )
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    recurring_bill: Mapped[Optional["RecurringBill"]] = relationship("RecurringBill", back_populates="liabilities")
    primary_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[primary_account_id],
        back_populates="liabilities"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        primaryjoin="Payment.liability_id == Liability.id",
        back_populates="liability",
        cascade="all, delete-orphan"
    )
    splits: Mapped[List["BillSplit"]] = relationship(
        "BillSplit",
        back_populates="liability",
        cascade="all, delete-orphan"
    )
    payment_schedules: Mapped[List["PaymentSchedule"]] = relationship(
        "PaymentSchedule",
        back_populates="liability",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Liability {self.name} due {self.due_date}>"
