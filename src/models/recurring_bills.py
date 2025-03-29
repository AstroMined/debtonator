from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseDBModel


class RecurringBill(BaseDBModel):
    """
    RecurringBill model representing template for recurring bills

    This is a pure data structure model for storing recurring bill information.
    Business logic like creating liabilities from recurring bills has been
    moved to the RecurringBillService according to ADR-012.
    """

    __tablename__ = "recurring_bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    day_of_month: Mapped[int]
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    auto_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    account = relationship("Account", back_populates="recurring_bills")
    category = relationship("Category")
    liabilities = relationship(
        "Liability", back_populates="recurring_bill", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RecurringBill {self.bill_name} ${self.amount:.2f}>"

    # Business logic for creating liabilities from recurring bills has been moved
    # to RecurringBillService.create_liability_from_recurring method according to ADR-012
