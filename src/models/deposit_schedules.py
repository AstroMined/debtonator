from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now, naive_utc_from_date

class DepositSchedule(BaseDBModel):
    """
    Model for scheduling income deposits.
    All datetime fields are stored as naive UTC, with timezone validation enforced
    through Pydantic schemas.
    """
    __tablename__ = "deposit_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    income_id: Mapped[int] = mapped_column(ForeignKey("income.id"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    schedule_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        doc="Scheduled deposit date (naive UTC). Use naive_utc_from_date to create."
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_pattern: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # Relationships
    income: Mapped["Income"] = relationship("Income", back_populates="deposit_schedules")
    account: Mapped["Account"] = relationship("Account", back_populates="deposit_schedules")
