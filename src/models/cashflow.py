from datetime import date
from decimal import Decimal
from sqlalchemy import Date, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..database.base import Base

class CashflowForecast(Base):
    """CashflowForecast model representing financial forecasts"""
    __tablename__ = "cashflow_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date]
    total_bills: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_income: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    forecast: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    min_14_day: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Minimum required funds for next 14 days"
    )
    min_30_day: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Minimum required funds for next 30 days"
    )
    min_60_day: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Minimum required funds for next 60 days"
    )
    min_90_day: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        comment="Minimum required funds for next 90 days"
    )
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, onupdate=date.today)

    # Create index on date for efficient lookups
    __table_args__ = (
        Index('idx_forecasts_date', 'date'),
    )

    def __repr__(self) -> str:
        return f"<CashflowForecast {self.date} balance=${self.balance}>"

    def calculate_daily_deficit(self, days: int = 14) -> Decimal:
        """Calculate daily deficit based on minimum amount needed"""
        min_amount = getattr(self, f"min_{days}_day")
        return min_amount / days if min_amount < 0 else Decimal(0)

    def calculate_yearly_deficit(self) -> Decimal:
        """Calculate yearly deficit based on daily deficit"""
        daily_deficit = self.calculate_daily_deficit()
        return daily_deficit * 365 if daily_deficit < 0 else Decimal(0)

    def calculate_required_income(self) -> Decimal:
        """Calculate required income considering 80% after tax"""
        yearly_deficit = self.calculate_yearly_deficit()
        return abs(yearly_deficit) / Decimal('0.8') if yearly_deficit < 0 else Decimal(0)

    def calculate_hourly_rate(self, hours_per_week: int = 40) -> Decimal:
        """Calculate required hourly rate to meet income needs"""
        required_income = self.calculate_required_income()
        return required_income / 52 / hours_per_week if required_income > 0 else Decimal(0)
