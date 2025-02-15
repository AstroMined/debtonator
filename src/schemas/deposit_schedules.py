from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict
from pydantic import BaseModel, Field

class DepositScheduleBase(BaseModel):
    income_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)
    schedule_date: date
    amount: Decimal = Field(..., gt=0)
    recurring: bool = False
    recurrence_pattern: Optional[Dict] = None
    status: str = Field(..., pattern="^(pending|completed)$")

class DepositScheduleCreate(DepositScheduleBase):
    pass

class DepositScheduleUpdate(BaseModel):
    schedule_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed)$")

class DepositSchedule(DepositScheduleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
