from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from sqlalchemy import String, Boolean, Numeric, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from .base_model import BaseDBModel
from src.models.payment_schedules import PaymentSchedule

class LiabilityStatus(str, Enum):
    """Enum for liability status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PAID = "paid"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class Liability(BaseDBModel):
    """
    Liability model representing a bill that needs to be paid.
    
    All datetime fields are stored in UTC format, with timezone validation enforced
    through Pydantic schemas.
    """
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    due_date: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("UTC")),
        doc="UTC timestamp of when the bill is due"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_bill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recurring_bills.id"), nullable=True)
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="bills")
    primary_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_pay_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For preferred payment date, method, etc.
    last_auto_pay_attempt: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        nullable=True,
        doc="UTC timestamp of the last auto-pay attempt"
    )
    auto_pay_enabled: Mapped[bool] = mapped_column(Boolean, default=False)  # Separate from auto_pay flag for temporary enable/disable
    status: Mapped[LiabilityStatus] = mapped_column(
        SQLEnum(LiabilityStatus),
        default=LiabilityStatus.PENDING
    )
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

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

    def __init__(self, **kwargs):
        # Ensure due_date is timezone-aware
        if 'due_date' in kwargs and kwargs['due_date'] is not None:
            if isinstance(kwargs['due_date'], datetime) and not kwargs['due_date'].tzinfo:
                kwargs['due_date'] = kwargs['due_date'].replace(tzinfo=ZoneInfo("UTC"))
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Liability {self.name} due {self.due_date}>"
