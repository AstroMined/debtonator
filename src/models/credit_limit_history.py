from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseDBModel
from src.utils.datetime_utils import naive_utc_now


class CreditLimitHistory(BaseDBModel):
    """
    Model for tracking credit limit changes over time

    This is a pure data structure model for recording the history of credit
    limit changes for credit accounts. Validation of account types is handled
    in the service layer, not in this model.

    Note: According to ADR-012, all business logic validation such as ensuring
    this can only be created for credit accounts has been moved to the service layer.
    """

    __tablename__ = "credit_limit_history"

    # Primary key and foreign key
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )

    # Credit limit fields
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Credit limit at this point in time"
    )
    effective_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=naive_utc_now,
        comment="Date when this credit limit became effective (naive UTC)",
    )
    reason: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Reason for credit limit change"
    )

    # Relationships
    account: Mapped["Account"] = relationship(
        "Account", back_populates="credit_limit_history"
    )

    def __repr__(self) -> str:
        return f"<CreditLimitHistory account_id={self.account_id} limit={self.credit_limit}>"
