"""
Earned Wage Access (EWA) account model for the polymorphic account hierarchy.

This module defines the EWAAccount model that inherits from the base Account model
and adds fields specific to EWA accounts (early access to earned wages).

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class EWAAccount(Account):
    """
    Earned Wage Access (EWA) account model representing early access to earned wages.

    Extends the base Account model with fields specific to EWA accounts,
    including provider details and fee information.
    """

    __tablename__ = "ewa_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="EWA service provider (Payactiv, DailyPay, etc.)",
    )
    max_advance_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Maximum percent of paycheck available for advance",
    )
    per_transaction_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Fee charged per advance transaction"
    )
    pay_period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="Start date of current pay period"
    )
    pay_period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="End date of current pay period"
    )
    next_payday: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="Date of next regular payday"
    )

    __mapper_args__ = {"polymorphic_identity": "ewa"}

    def __repr__(self) -> str:
        return f"<EWAAccount(id={self.id}, name={self.name}, provider={self.provider})>"
