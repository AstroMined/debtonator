from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class StatementHistory(Base):
    """Model for tracking account statement history"""
    __tablename__ = "statement_history"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Statement details
    statement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
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
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=True,
        comment="Payment due date"
    )
    
    # Timestamps
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, onupdate=date.today)
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="statement_history")

    def __repr__(self) -> str:
        return f"<StatementHistory {self.account_id} - {self.statement_date}>"
