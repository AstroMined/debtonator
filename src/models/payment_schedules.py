from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel

class PaymentSchedule(BaseDBModel):
    __tablename__ = "payment_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    liability_id: Mapped[int] = mapped_column(ForeignKey("liabilities.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    scheduled_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        comment="Scheduled payment date (naive UTC)"
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    auto_process: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),
        comment="Date when payment was processed (naive UTC)"
    )

    # Relationships
    liability: Mapped["Liability"] = relationship("Liability", back_populates="payment_schedules")
    account: Mapped["Account"] = relationship("Account", back_populates="payment_schedules")
