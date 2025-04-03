from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseDBModel

# from src.models.accounts import Account
# from src.models.liabilities import Liability


class PaymentSchedule(BaseDBModel):
    __tablename__ = "payment_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    liability_id: Mapped[int] = mapped_column(
        ForeignKey("liabilities.id"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    scheduled_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        doc="Scheduled payment date (naive UTC). Use naive_utc_from_date to create.",
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    auto_process: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),
        doc="Date when payment was processed (naive UTC). Set using naive_utc_now.",
    )

    # Relationships
    liability: Mapped["Liability"] = relationship(
        "Liability", back_populates="payment_schedules"
    )
    account: Mapped["Account"] = relationship(
        "Account", back_populates="payment_schedules"
    )
