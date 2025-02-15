from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class AccountBalance(BaseModel):
    account_id: int
    name: str
    type: str
    current_balance: Decimal
    available_credit: Optional[Decimal] = None
    total_limit: Optional[Decimal] = None

class RealtimeCashflow(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    account_balances: List[AccountBalance]
    total_available_funds: Decimal
    total_available_credit: Decimal
    total_liabilities_due: Decimal
    net_position: Decimal
    next_bill_due: Optional[datetime] = None
    days_until_next_bill: Optional[int] = None
    minimum_balance_required: Decimal
    projected_deficit: Optional[Decimal] = None

class RealtimeCashflowResponse(BaseModel):
    data: RealtimeCashflow
    last_updated: datetime = Field(default_factory=datetime.utcnow)
