from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now


class BalanceReconciliation(BaseDBModel):
    """Model for tracking balance reconciliation history"""

    __tablename__ = "balance_reconciliation"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    previous_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    adjustment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255))
    reconciliation_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=naive_utc_now,
        comment="Date of balance reconciliation (naive UTC)",
    )

    # Relationships
    account: Mapped["Account"] = relationship(
        "Account", back_populates="balance_reconciliations"
    )

    def __repr__(self) -> str:
        return f"<BalanceReconciliation(id={self.id}, account_id={self.account_id}, adjustment_amount={self.adjustment_amount})>"
