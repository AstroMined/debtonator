from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from .base_model import BaseDBModel

class RecurringBill(BaseDBModel):
    """RecurringBill model representing template for recurring bills"""
    __tablename__ = "recurring_bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    day_of_month: Mapped[int]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    account = relationship("Account", back_populates="recurring_bills")
    category = relationship("Category")
    liabilities = relationship("Liability", back_populates="recurring_bill", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RecurringBill {self.bill_name} ${self.amount}>"

    def create_liability(self, month: str, year: int) -> "Liability":
        """Create a new Liability instance from this recurring bill template"""
        from .liabilities import Liability  # Import here to avoid circular imports
        
        liability = Liability(
            name=self.bill_name,
            amount=self.amount,
            due_date=datetime(year, int(month), self.day_of_month),
            primary_account_id=self.account_id,
            category_id=self.category_id,
            auto_pay=self.auto_pay,
            recurring=True,
            recurring_bill_id=self.id,
            category=self.category  # Set the relationship directly
        )
        return liability
