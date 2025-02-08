from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class BillBase(BaseModel):
    month: str = Field(..., description="Month of the bill")
    day_of_month: int = Field(..., description="Day of the month the bill is due")
    bill_name: str = Field(..., description="Name of the bill")
    amount: Decimal = Field(..., description="Amount of the bill")
    account: str = Field(..., description="Account used for payment (AMEX, UFCU, Unlimited)")
    auto_pay: bool = Field(default=False, description="Whether the bill is on auto-pay")
    
class BillCreate(BillBase):
    pass

class BillUpdate(BillBase):
    month: Optional[str] = None
    day_of_month: Optional[int] = None
    bill_name: Optional[str] = None
    amount: Optional[Decimal] = None
    account: Optional[str] = None
    auto_pay: Optional[bool] = None
    paid: Optional[bool] = None
    paid_date: Optional[date] = None

class Bill(BillBase):
    id: int
    due_date: date
    paid_date: Optional[date] = None
    up_to_date: bool
    paid: bool = False
    amex_amount: Optional[Decimal] = None
    unlimited_amount: Optional[Decimal] = None
    ufcu_amount: Optional[Decimal] = None

    class Config:
        from_attributes = True

class BillDateRange(BaseModel):
    start_date: date = Field(..., description="Start date for bill range")
    end_date: date = Field(..., description="End date for bill range")
