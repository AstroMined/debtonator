from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel

class RecurringIncome(BaseDBModel):
    """RecurringIncome model representing template for recurring income"""
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

    def create_income_entry(self, month: int, year: int) -> "Income":
        """Create a new Income instance from this recurring income template"""
        from .income import Income  # Import here to avoid circular imports
        
        income_entry = Income(
            source=self.source,
            amount=self.amount,
            date=datetime(year, month, self.day_of_month),
            account_id=self.account_id,
            category_id=self.category_id,
            deposited=self.auto_deposit,
            recurring=True,
            recurring_income_id=self.id,
            category=self.category  # Set the relationship directly
        )
        return income_entry
