from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.payment_schedules import PaymentSchedule

from src.models.base_model import BaseDBModel
from src.utils.datetime_utils import naive_utc_now


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

    This model focuses purely on data structure, with all validation and business logic
    handled at the schema and service layers respectively:
    - Data validation: Enforced through Pydantic schemas
    - Business logic: Implemented in the liability service
    - Datetime fields: Stored in UTC format, validated by schemas
    - Auto-pay logic: Managed by service layer
    - Status transitions: Controlled by service layer
    """

    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    due_date: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        nullable=False,
        default=naive_utc_now,
        doc="UTC timestamp of when the bill is due",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_bill_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recurring_bills.id"), nullable=True
    )
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="JSON structure defining recurrence rules. Validation handled by schema.",
    )
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="bills")
    primary_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))

    # Auto-pay configuration - all validation and processing handled by service layer
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_pay_settings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="JSON configuration for auto-pay preferences. Validation in schema layer.",
    )
    last_auto_pay_attempt: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        nullable=True,
        doc="UTC timestamp of the last auto-pay attempt",
    )
    auto_pay_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Temporary enable/disable flag for auto-pay. State transitions managed by service.",
    )

    # Status fields - all transitions and validation handled by service layer
    status: Mapped[LiabilityStatus] = mapped_column(
        SQLEnum(LiabilityStatus),
        default=LiabilityStatus.PENDING,
        doc="Current state of the liability. Transitions managed by service layer.",
    )
    paid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Payment status flag. Updates managed by service layer.",
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, doc="Active status flag. State managed by service layer."
    )

    # Relationships
    recurring_bill: Mapped[Optional["RecurringBill"]] = relationship(
        "RecurringBill", back_populates="liabilities"
    )
    primary_account: Mapped["Account"] = relationship(
        "Account", foreign_keys=[primary_account_id], back_populates="liabilities"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        primaryjoin="Payment.liability_id == Liability.id",
        back_populates="liability",
        cascade="all, delete-orphan",
    )
    splits: Mapped[List["BillSplit"]] = relationship(
        "BillSplit", back_populates="liability", cascade="all, delete-orphan"
    )
    payment_schedules: Mapped[List["PaymentSchedule"]] = relationship(
        "PaymentSchedule", back_populates="liability", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Liability {self.name} due {self.due_date}>"
