from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class RecurringBill(Base):
    """RecurringBill model representing template for recurring bills"""
    __tablename__ = "recurring_bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    day_of_month: Mapped[int]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    account = relationship("Account", back_populates="recurring_bills")

    def __repr__(self) -> str:
        return f"<RecurringBill {self.bill_name} ${self.amount}>"

    def create_liability(self, month: str, year: int) -> "Liability":
        """Create a new Liability instance from this recurring bill template"""
        from .liabilities import Liability  # Import here to avoid circular imports
        
        return Liability(
            name=self.bill_name,
            amount=self.amount,
            due_date=date(year, int(month), self.day_of_month),
            primary_account_id=self.account_id,
            category="Recurring",  # Default category for recurring bills
            auto_pay=self.auto_pay
        )
