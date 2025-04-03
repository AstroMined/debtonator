"""
Checking account model for the polymorphic account hierarchy.

This module defines the CheckingAccount model that inherits from the base Account model
and adds fields specific to checking accounts.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class CheckingAccount(Account):
    """
    Checking account model representing a transaction account for day-to-day banking.

    Extends the base Account model with fields specific to checking accounts,
    including routing information and overdraft details.
    """

    __tablename__ = "checking_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    routing_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Account routing number"
    )
    has_overdraft_protection: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether overdraft protection is enabled",
    )
    overdraft_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4),
        nullable=True,
        comment="Maximum overdraft amount (when protection is enabled)",
    )
    monthly_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Monthly account maintenance fee"
    )
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Annual interest rate (if interest-bearing)",
    )

    # International banking fields
    iban: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="International Bank Account Number"
    )
    swift_bic: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="SWIFT/BIC code for international transfers"
    )
    sort_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="Sort code (used in UK and other countries)"
    )
    branch_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="Branch code (used in various countries)"
    )
    account_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="local",
        comment="Account number format (local, iban, etc.)",
    )

    __mapper_args__ = {"polymorphic_identity": "checking"}

    def __repr__(self) -> str:
        return f"<CheckingAccount(id={self.id}, name={self.name})>"
