from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now

class BalanceHistory(BaseDBModel):
    __tablename__ = "balance_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    available_credit: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=10, scale=2))
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(),
        default=naive_utc_now,
        nullable=False,
        comment="Time of balance record (naive UTC)"
    )

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="balance_history")


# Add this to Account model in src/models/accounts.py:
# balance_history = relationship("BalanceHistory", back_populates="account", cascade="all, delete-orphan")
