from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
import enum

from ..database.base import Base

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionHistory(Base):
    """Model for tracking account transactions"""
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(String, nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return (
            f"<TransactionHistory(id={self.id}, "
            f"account_id={self.account_id}, "
            f"amount={self.amount}, "
            f"type={self.transaction_type}, "
            f"date={self.transaction_date})>"
        )
