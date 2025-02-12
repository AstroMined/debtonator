from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database.base import Base

class BalanceReconciliation(Base):
    """Model for tracking balance reconciliation history"""
    __tablename__ = "balance_reconciliation"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    previous_balance = Column(DECIMAL(10, 2), nullable=False)
    new_balance = Column(DECIMAL(10, 2), nullable=False)
    adjustment_amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String(255))
    reconciliation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="balance_reconciliations")
    
    def __repr__(self) -> str:
        return f"<BalanceReconciliation(id={self.id}, account_id={self.account_id}, adjustment_amount={self.adjustment_amount})>"
