from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now

class RecurringIncome(BaseDBModel):
    """
    RecurringIncome model representing template for recurring income.
    
    This is a pure data structure model that follows ADR-012 by not containing
    any business logic or validation. The creation of actual income entries from
    this template is handled by the RecurringIncomeService.
    """
    __tablename__ = "recurring_income"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    day_of_month: Mapped[int]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("income_categories.id"), nullable=True)
    auto_deposit: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    account = relationship("Account", back_populates="recurring_income")
    category = relationship("IncomeCategory")
    income_entries = relationship("Income", back_populates="recurring_income", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RecurringIncome {self.source} ${self.amount}>"
