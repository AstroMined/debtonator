from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

class PaymentScheduleBase(BaseModel):
    liability_id: int
    scheduled_date: date
    amount: float = Field(gt=0)
    account_id: int
    description: Optional[str] = None
    auto_process: bool = False

class PaymentScheduleCreate(PaymentScheduleBase):
    pass

class PaymentSchedule(PaymentScheduleBase):
    id: int
    processed: bool = False
    processed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
