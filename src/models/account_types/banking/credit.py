"""
Credit account model for the polymorphic account hierarchy.

This module defines the CreditAccount model that inherits from the base Account model
and adds fields specific to credit accounts.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class CreditAccount(Account):
    """
    Credit account model representing a revolving credit account.

    Extends the base Account model with fields specific to credit accounts,
    including credit limits, statement details, and interest rates.
    """

    __tablename__ = "credit_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Total credit limit"
    )
    statement_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Current statement balance"
    )
    statement_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="Payment due date for current statement"
    )
    minimum_payment: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Minimum payment due"
    )
    apr: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4), nullable=True, comment="Annual Percentage Rate"
    )
    annual_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Annual card fee"
    )
    rewards_program: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Rewards program name"
    )
    autopay_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Autopay status (none, minimum, full_balance, fixed_amount)",
    )
    last_statement_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(), nullable=True, comment="Date of last statement"
    )

    __mapper_args__ = {"polymorphic_identity": "credit"}

    def __repr__(self) -> str:
        return f"<CreditAccount(id={self.id}, name={self.name})>"
