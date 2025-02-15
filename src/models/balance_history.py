from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.database.base import Base


class BalanceHistory(Base):
    __tablename__ = "balance_history"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    balance = Column(Numeric(precision=10, scale=2), nullable=False)
    available_credit = Column(Numeric(precision=10, scale=2))
    is_reconciled = Column(Boolean, default=False, nullable=False)
    notes = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    account = relationship("Account", back_populates="balance_history")


# Add this to Account model in src/models/accounts.py:
# balance_history = relationship("BalanceHistory", back_populates="account", cascade="all, delete-orphan")
