from datetime import date
from decimal import Decimal
from typing import List
from sqlalchemy import String, Date, Boolean, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

class DepositSchedule(Base):
    __tablename__ = "deposit_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    income_id: Mapped[int] = mapped_column(ForeignKey("income.id"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    schedule_date: Mapped[date]
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_pattern: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    income = relationship("Income", back_populates="deposit_schedules")
    account = relationship("Account", back_populates="deposit_schedules")
