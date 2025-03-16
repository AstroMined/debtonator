from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now


class Payment(BaseDBModel):
    """
    Payment model representing a transaction made to pay a bill or other expense.

    All datetime fields are stored in UTC format, with timezone validation enforced
    through Pydantic schemas.
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    liability_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("liabilities.id"), nullable=True
    )
    income_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("income.id"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        default=naive_utc_now,
        doc="UTC timestamp of when the payment was made",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100))
    # Relationships
    liability = relationship("Liability", back_populates="payments")
    income = relationship("Income", back_populates="payments")
    sources: Mapped[List["PaymentSource"]] = relationship(
        "PaymentSource", back_populates="payment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Payment {self.amount} on {self.payment_date}>"


class PaymentSource(BaseDBModel):
    """PaymentSource model representing an account used to make a payment"""

    __tablename__ = "payment_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE")
    )
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    # Relationships
    payment = relationship("Payment", back_populates="sources")
    account = relationship("Account", back_populates="payment_sources")

    def __repr__(self) -> str:
        return f"<PaymentSource {self.amount} from account {self.account_id}>"
