from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel

class StatementHistory(BaseDBModel):
    """Model for tracking account statement history"""
    __tablename__ = "statement_history"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Statement details
    statement_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("UTC")),
        server_default="CURRENT_TIMESTAMP",
        comment="Date of the statement"
    )
    statement_balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Balance on statement date"
    )
    minimum_payment: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Minimum payment due"
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=lambda: datetime.now(ZoneInfo("UTC")) + timedelta(days=25),
        comment="Payment due date"
    )
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="statement_history")

    def __repr__(self) -> str:
        return f"<StatementHistory {self.account_id} - {self.statement_date}>"
