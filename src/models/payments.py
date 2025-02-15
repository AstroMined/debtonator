from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Date, Numeric, Text, DateTime, ForeignKey
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class Payment(Base):
    """Payment model representing a transaction made to pay a bill or other expense"""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    liability_id: Mapped[Optional[int]] = mapped_column(ForeignKey("liabilities.id"), nullable=True)
    income_id: Mapped[Optional[int]] = mapped_column(ForeignKey("income.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(ZoneInfo("UTC")), 
        onupdate=lambda: datetime.now(ZoneInfo("UTC"))
    )

    # Relationships
    liability = relationship("Liability", back_populates="payments")
    income = relationship("Income", back_populates="payments")
    sources: Mapped[List["PaymentSource"]] = relationship(
        "PaymentSource",
        back_populates="payment",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Payment {self.amount} on {self.payment_date}>"


class PaymentSource(Base):
    """PaymentSource model representing an account used to make a payment"""
    __tablename__ = "payment_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(ZoneInfo("UTC")), 
        onupdate=lambda: datetime.now(ZoneInfo("UTC"))
    )

    # Relationships
    payment = relationship("Payment", back_populates="sources")
    account = relationship("Account", back_populates="payment_sources")

    def __repr__(self) -> str:
        return f"<PaymentSource {self.amount} from account {self.account_id}>"
