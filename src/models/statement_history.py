from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_now

class StatementHistory(BaseDBModel):
    """Model for tracking account statement history"""
    __tablename__ = "statement_history"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Statement details
    statement_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=naive_utc_now,
        comment="Date of the statement (naive UTC)"
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
        DateTime(),
        nullable=True,
        comment="Payment due date (naive UTC)"
    )

    def __init__(self, **kwargs):
        # If due_date not provided, set it to 25 days after statement_date
        if 'due_date' not in kwargs and 'statement_date' in kwargs:
            kwargs['due_date'] = kwargs['statement_date'] + timedelta(days=25)
        super().__init__(**kwargs)
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="statement_history")

    def __repr__(self) -> str:
        return f"<StatementHistory {self.account_id} - {self.statement_date}>"
