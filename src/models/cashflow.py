from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..database.base import Base

class CashflowForecast(Base):
    """Model for storing cashflow forecasts"""
    __tablename__ = "cashflow_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    forecast_date: Mapped[date] = mapped_column(Date)
    total_bills: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_income: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    forecast: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    min_14_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    min_30_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    min_60_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    min_90_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    daily_deficit: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    yearly_deficit: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    required_income: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    hourly_rate_40: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    hourly_rate_30: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    hourly_rate_20: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[date] = mapped_column(Date, default=lambda: date.today())
    updated_at: Mapped[date] = mapped_column(Date, default=lambda: date.today(), onupdate=lambda: date.today())

    # Create indexes for efficient lookups
    __table_args__ = (
        Index('idx_cashflow_forecast_date', 'forecast_date'),
    )

    def __repr__(self) -> str:
        return f"<CashflowForecast {self.forecast_date} balance={self.balance}>"

    def calculate_deficits(self) -> None:
        """Calculate daily and yearly deficits based on minimum required amounts"""
        min_amount = min(self.min_14_day, self.min_30_day, self.min_60_day, self.min_90_day)
        self.daily_deficit = min_amount / 14 if min_amount < 0 else Decimal(0)
        self.yearly_deficit = self.daily_deficit * 365

    def calculate_required_income(self) -> None:
        """Calculate required income considering 80% after tax"""
        self.required_income = abs(self.yearly_deficit) / Decimal('0.8')

    def calculate_hourly_rates(self) -> None:
        """Calculate hourly rates for different work hours per week"""
        weekly_required = self.required_income / 52
        self.hourly_rate_40 = weekly_required / 40
        self.hourly_rate_30 = weekly_required / 30
        self.hourly_rate_20 = weekly_required / 20
