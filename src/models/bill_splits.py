from datetime import date
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base

class BillSplit(Base):
    """Model representing a bill payment split across multiple accounts"""
    __tablename__ = "bill_splits"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("liabilities.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Amount of the bill allocated to this account"
    )
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Relationships
    bill = relationship("Liability", back_populates="splits")
    account = relationship("Account", back_populates="bill_splits")

    # Create indexes for efficient lookups
    __table_args__ = (
        Index('idx_bill_splits_bill_id', 'bill_id'),
        Index('idx_bill_splits_account_id', 'account_id'),
    )

    def __repr__(self) -> str:
        return f"<BillSplit bill_id={self.bill_id} account_id={self.account_id} amount={self.amount}>"
