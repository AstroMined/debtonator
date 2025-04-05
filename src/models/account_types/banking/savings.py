"""
Savings account model for the polymorphic account hierarchy.

This module defines the SavingsAccount model that inherits from the base Account model
and adds fields specific to savings accounts.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class SavingsAccount(Account):
    """
    Savings account model representing an interest-bearing account for saving money.

    Extends the base Account model with fields specific to savings accounts,
    including interest rates and withdrawal limits.
    """

    __tablename__ = "savings_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4), nullable=True, comment="Annual interest rate"
    )
    routing_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Bank routing number"
    )
    compound_frequency: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Interest compounding frequency (daily, monthly, quarterly, annually)",
    )
    interest_earned_ytd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Interest earned year-to-date"
    )
    withdrawal_limit: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Maximum number of withdrawals per period"
    )
    minimum_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Minimum balance required to avoid fees"
    )

    __mapper_args__ = {"polymorphic_identity": "savings"}

    def __repr__(self) -> str:
        return f"<SavingsAccount(id={self.id}, name={self.name})>"
