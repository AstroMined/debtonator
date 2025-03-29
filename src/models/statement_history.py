from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base_model import BaseDBModel
from src.utils.datetime_utils import naive_utc_now


class StatementHistory(BaseDBModel):
    """
    Model for tracking account statement history.

    This is a pure data structure model that follows ADR-012 by not containing
    any business logic or validation. Any calculation of due dates or validation
    of statement fields is handled in the StatementService.
    """

    __tablename__ = "statement_history"

    # Primary key and foreign key
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )

    # Statement details
    statement_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=naive_utc_now,
        comment="Date of the statement (naive UTC)",
    )
    statement_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Balance on statement date"
    )
    minimum_payment: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=True, comment="Minimum payment due"
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=True, comment="Payment due date (naive UTC)"
    )

    # Relationships
    account: Mapped["Account"] = relationship(
        "Account", back_populates="statement_history"
    )

    def __repr__(self) -> str:
        return f"<StatementHistory {self.account_id} - {self.statement_date}>"
