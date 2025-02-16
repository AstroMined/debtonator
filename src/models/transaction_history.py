from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionHistory(BaseDBModel):
    """
    Model for tracking account transactions.
    
    - Inherits `created_at` and `updated_at` from BaseDBModel, which are naive columns 
      stored as UTC.
    - The `transaction_date` here is the actual time of the transaction, possibly coming
      from an external data source, so it may differ from the `created_at` or `updated_at`.
    - All datetime columns are stored as naive UTC; Pydantic schemas enforce 
      the UTC requirement.
    """

    __tablename__ = "transaction_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False
    )
    description: Mapped[str] = mapped_column(String, nullable=True)

    # Store as a naive datetime in the DB. Pydantic will enforce UTC semantics.
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        doc="Time of the actual transaction (naive, but enforced as UTC by Pydantic)."
    )

    # Relationship
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return (
            f"<TransactionHistory(id={self.id}, "
            f"account_id={self.account_id}, "
            f"amount={self.amount}, "
            f"type={self.transaction_type}, "
            f"transaction_date={self.transaction_date})>"
        )
