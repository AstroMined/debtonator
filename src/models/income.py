from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel, naive_utc_from_date, naive_utc_now


class Income(BaseDBModel):
    """
    Income model representing an income record.

    This model serves as a pure data structure for income records, with all business logic
    and validation handled by the service layer and Pydantic schemas respectively.

    Key responsibilities:
    - Store income record data
    - Define relationships with other models
    - Maintain data integrity through constraints

    Business logic, such as undeposited amount calculations and balance updates,
    is handled by the IncomeService to maintain proper separation of concerns.

    All datetime fields are stored in UTC format, with timezone validation enforced
    through Pydantic schemas.

    Note: This model follows the project's validation standardization (ADR-012),
    keeping the model focused on data structure while moving all validation and
    business logic to the appropriate layers.
    """

    __tablename__ = "income"

    # Core fields
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(),  # No timezone parameter - enforced by schema
        doc="UTC timestamp of when the income was received. Use naive_utc_from_date or naive_utc_now to create.",
    )
    source: Mapped[str] = mapped_column(
        String(255), doc="Name or description of the income source"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        doc="Income amount with 4 decimal precision for calculations. Display validation handled by schema.",
    )

    # Status fields
    deposited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Indicates whether the income has been deposited into an account",
    )
    undeposited_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        default=0,
        doc="Calculated field maintained by service layer based on deposit status",
    )
    # Account and Category relationships
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        doc="ID of the account this income is associated with",
    )
    account = relationship(
        "Account", back_populates="income", doc="Reference to the associated account"
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("income_categories.id"),
        nullable=True,
        doc="Optional ID of the income category for classification",
    )
    category = relationship(
        "IncomeCategory", doc="Reference to the optional income category"
    )

    # Recurring Income relationship
    recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Indicates if this is part of a recurring income pattern",
    )
    recurring_income_id: Mapped[int] = mapped_column(
        ForeignKey("recurring_income.id"),
        nullable=True,
        doc="Optional ID of the associated recurring income pattern",
    )
    recurring_income = relationship(
        "RecurringIncome",
        back_populates="income_entries",
        doc="Reference to the optional recurring income pattern",
    )

    # Payment and Schedule Relationships
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="income",
        doc="List of payments associated with this income",
    )
    deposit_schedules: Mapped[List["DepositSchedule"]] = relationship(
        "DepositSchedule",
        back_populates="income",
        doc="List of deposit schedules for this income",
    )

    # Create indexes and constraints
    __table_args__ = (
        Index("idx_income_date", "date"),
        Index("idx_income_deposited", "deposited"),
        CheckConstraint("amount >= 0", name="ck_income_positive_amount"),
    )

    def __repr__(self) -> str:
        return f"<Income {self.source} {self.amount:.2f}>"
