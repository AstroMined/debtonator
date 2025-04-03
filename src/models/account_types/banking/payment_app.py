"""
Payment app account model for the polymorphic account hierarchy.

This module defines the PaymentAppAccount model that inherits from the base Account model
and adds fields specific to payment app accounts (PayPal, Venmo, Cash App, etc.).

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.accounts import Account


class PaymentAppAccount(Account):
    """
    Payment app account model representing a digital wallet (PayPal, Venmo, Cash App, etc.).

    Extends the base Account model with fields specific to payment apps,
    including platform details and linked accounts.
    """

    __tablename__ = "payment_app_accounts"

    id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), primary_key=True)
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Payment platform (PayPal, Venmo, Cash App, etc.)",
    )
    has_debit_card: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether account has an associated debit card",
    )
    card_last_four: Mapped[Optional[str]] = mapped_column(
        String(4), nullable=True, comment="Last four digits of associated card (if any)"
    )
    linked_account_ids: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Comma-separated list of linked account IDs"
    )
    supports_direct_deposit: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether account supports direct deposit",
    )
    supports_crypto: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether account supports cryptocurrency",
    )

    __mapper_args__ = {"polymorphic_identity": "payment_app"}

    def __repr__(self) -> str:
        return f"<PaymentAppAccount(id={self.id}, name={self.name}, platform={self.platform})>"
