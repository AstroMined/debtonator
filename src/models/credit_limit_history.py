from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from .base_model import BaseDBModel, naive_utc_now

class CreditLimitHistory(BaseDBModel):
    """Model for tracking credit limit changes over time"""
    __tablename__ = "credit_limit_history"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Credit limit fields
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Credit limit at this point in time"
    )
    effective_date: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=naive_utc_now,
        comment="Date when this credit limit became effective (naive UTC)"
    )
    reason: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="Reason for credit limit change"
    )
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="credit_limit_history")

    def __repr__(self) -> str:
        return f"<CreditLimitHistory account_id={self.account_id} limit={self.credit_limit}>"

@event.listens_for(CreditLimitHistory, 'before_insert')
@event.listens_for(CreditLimitHistory, 'before_update')
def validate_credit_account(mapper, connection, target):
    """Ensure credit limit history can only be created for credit accounts."""
    session = Session(bind=connection)
    from .accounts import Account  # Import here to avoid circular imports
    
    account = session.get(Account, target.account_id)
    if account and account.type != "credit":
        raise ValueError("Credit limit history can only be created for credit accounts")
