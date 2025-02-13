from datetime import date, datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Date
from sqlalchemy.orm import relationship

from src.database.base import Base

class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id = Column(Integer, primary_key=True)
    liability_id = Column(Integer, ForeignKey("liabilities.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String)
    auto_process = Column(Boolean, default=False, nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    processed_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    liability = relationship("Liability", back_populates="payment_schedules")
    account = relationship("Account", back_populates="payment_schedules")
