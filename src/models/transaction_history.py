from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from .base_model import BaseDBModel

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionHistory(BaseDBModel):
    """Model for tracking account transactions"""
    __tablename__ = "transaction_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return (
            f"<TransactionHistory(id={self.id}, "
            f"account_id={self.account_id}, "
            f"amount={self.amount}, "
            f"type={self.transaction_type}, "
            f"date={self.transaction_date})>"
        )
