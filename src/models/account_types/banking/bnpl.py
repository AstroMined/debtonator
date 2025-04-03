"""
Buy Now Pay Later (BNPL) account model for the polymorphic account hierarchy.

This module defines the BNPLAccount model that inherits from the base Account model
and adds fields specific to BNPL accounts (Affirm, Klarna, Afterpay, etc.).

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class BNPLAccount(Account):
    """
    Buy Now Pay Later (BNPL) account model representing an installment plan for purchases.

    Extends the base Account model with fields specific to BNPL accounts,
    including installment details and payment tracking.
    """

    __tablename__ = "bnpl_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    original_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Original purchase amount"
    )
    installment_count: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Total number of installments"
    )
    installments_paid: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of installments already paid",
    )
    installment_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Amount per installment"
    )
    payment_frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Payment frequency (weekly, biweekly, monthly)",
    )
    next_payment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="Date of next payment due"
    )
    promotion_info: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Promotional details (e.g., '0% interest for 6 months')",
    )
    late_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Late payment fee amount"
    )
    bnpl_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="BNPL service provider (Affirm, Klarna, Afterpay, etc.)",
    )

    __mapper_args__ = {"polymorphic_identity": "bnpl"}

    def __repr__(self) -> str:
        return f"<BNPLAccount(id={self.id}, name={self.name}, provider={self.bnpl_provider})>"
