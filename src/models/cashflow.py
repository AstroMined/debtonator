from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseDBModel


class CashflowForecast(BaseDBModel):
    """Model for storing cashflow forecasts

    This is a pure data storage model with no business logic.
    All calculation methods have been moved to the service layer.
    """

    __tablename__ = "cashflow_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    forecast_date: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, doc="UTC timestamp of the forecast (naive UTC)"
    )
    total_bills: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    total_income: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    forecast: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    min_14_day: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    min_30_day: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    min_60_day: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    min_90_day: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    daily_deficit: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    yearly_deficit: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    required_income: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    hourly_rate_40: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    hourly_rate_30: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    hourly_rate_20: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    # Create indexes for efficient lookups
    __table_args__ = (Index("idx_cashflow_forecast_date", "forecast_date"),)

    def __repr__(self) -> str:
        return f"<CashflowForecast {self.forecast_date} balance={self.balance}>"
