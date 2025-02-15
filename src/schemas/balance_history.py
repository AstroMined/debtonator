from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BalanceHistoryBase(BaseModel):
    account_id: int = Field(..., gt=0)
    balance: Decimal = Field(..., decimal_places=2)
    available_credit: Optional[Decimal] = Field(None, decimal_places=2)
    is_reconciled: bool = Field(default=False)
    notes: Optional[str] = None


class BalanceHistoryCreate(BalanceHistoryBase):
    pass


class BalanceHistory(BalanceHistoryBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BalanceTrend(BaseModel):
    account_id: int
    start_date: datetime
    end_date: datetime
    start_balance: Decimal
    end_balance: Decimal
    net_change: Decimal
    average_balance: Decimal
    min_balance: Decimal
    max_balance: Decimal
    trend_direction: str  # "increasing", "decreasing", or "stable"
    volatility: Decimal  # Standard deviation of balance changes
