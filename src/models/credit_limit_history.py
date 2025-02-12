from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class CreditLimitHistory(Base):
    """Model for tracking credit limit changes over time"""
    __tablename__ = "credit_limit_history"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Credit limit fields
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Credit limit at this point in time"
    )
    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date when this credit limit became effective"
    )
    reason: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Reason for credit limit change"
    )
    
    # Timestamps
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="credit_limit_history")

    def __repr__(self) -> str:
        return f"<CreditLimitHistory account_id={self.account_id} limit={self.credit_limit}>"
